import secrets
import string
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import hash_password
from app.models.user import User


class RegistrationError(Exception):
    """Raised for any business-rule violation during user registration."""


def _generate_referral_code(length: int = 10) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


async def _total_user_count(db: AsyncSession) -> int:
    result = await db.execute(select(func.count()).select_from(User))
    return result.scalar_one()


async def register_root_user(
    db: AsyncSession, full_name: str, email: str, password: str,
    phone_number: str | None = None, nid: str | None = None
) -> User:
    """Registers the single Layer 0 root. Fails if a root already exists."""
    existing_root = await db.execute(select(User).where(User.layer_level == 0))
    if existing_root.scalar_one_or_none() is not None:
        raise RegistrationError("Root user already exists. Use a referral code to register.")

    total = await _total_user_count(db)
    if total >= settings.max_total_users:
        raise RegistrationError("Platform has reached its 11,111 user capacity.")

    referral_code = _generate_referral_code()
    root = User(
        id=uuid.uuid4(),
        full_name=full_name,
        email=email,
        hashed_password=hash_password(password),
        phone_number=phone_number,
        nid=nid,
        referral_code=referral_code,
        layer_level=0,
        parent_id=None,
        node_path="Top",
        child_count=0,
    )
    db.add(root)
    await db.flush()
    return root


async def register_user_with_referral(
    db: AsyncSession, full_name: str, email: str, password: str, parent_referral_code: str,
    phone_number: str | None = None, nid: str | None = None
) -> User:
    """Registers a Layer k>=1 user under the parent identified by parent_referral_code.

    Locks the parent row FOR UPDATE to serialize concurrent child_count increments
    and re-checks the global capacity + child-count invariants inside that lock.
    """
    if not phone_number or not nid:
        raise RegistrationError("Phone number and NID are required for non-root users.")

    total = await _total_user_count(db)
    if total >= settings.max_total_users:
        raise RegistrationError("Platform has reached its 11,111 user capacity.")

    result = await db.execute(
        select(User).where(User.referral_code == parent_referral_code).with_for_update()
    )
    parent = result.scalar_one_or_none()
    if parent is None:
        raise RegistrationError("Invalid referral code.")
    if not parent.is_active:
        raise RegistrationError("Referring user is not active.")
    if parent.child_count >= settings.max_children_per_node:
        raise RegistrationError("Referral code has reached its 10-child capacity and is invalidated.")

    new_layer = parent.layer_level + 1
    if new_layer > settings.max_layer:
        raise RegistrationError("Maximum tree depth (Layer 4) exceeded; leaf nodes cannot have children.")

    child_index = parent.child_count + 1
    node_path = f"{parent.node_path}.L{new_layer}_{child_index}"

    referral_code = _generate_referral_code()
    user = User(
        id=uuid.uuid4(),
        full_name=full_name,
        email=email,
        hashed_password=hash_password(password),
        phone_number=phone_number,
        nid=nid,
        referral_code=referral_code,
        layer_level=new_layer,
        parent_id=parent.id,
        node_path=node_path,
        child_count=0,
    )
    parent.child_count = child_index

    db.add(user)
    await db.flush()
    return user


async def get_direct_ancestors(db: AsyncSession, user: User) -> list[User]:
    """Returns the direct upward lineage of `user`, ordered nearest-parent-first,
    using the LTREE node_path for a single indexed ancestor-query instead of
    walking parent_id one row at a time.
    """
    if user.layer_level == 0 or not user.parent_id:
        return []

    # `@>` is the LTREE "is ancestor of" operator: rows whose node_path is an
    # ancestor of user.node_path, resolved in one indexed query (GIST on node_path).
    result = await db.execute(
        select(User)
        .where(User.node_path.op("@>")(user.node_path))
        .where(User.id != user.id)
        .order_by(User.layer_level.desc())
    )
    return list(result.scalars().all())


async def get_team_report(db: AsyncSession, user: User) -> tuple[list[User], list[User]]:
    """Returns (direct_children, deeper_descendants) for `user`.

    Uses LTREE `<@` operator (descendant-of) to find all descendants in one indexed query,
    then partitions them into immediate children (parent_id == user.id) and deeper descendants.
    """
    if user.layer_level >= settings.max_layer:
        return [], []

    # `<@` is the LTREE "is descendant of or equal" operator. Exclude self.
    result = await db.execute(
        select(User)
        .where(User.node_path.op("<@")(user.node_path))
        .where(User.id != user.id)
        .order_by(User.layer_level, User.full_name)
    )
    all_descendants = list(result.scalars().all())

    direct_children = [d for d in all_descendants if d.parent_id == user.id]
    deeper_descendants = [d for d in all_descendants if d.parent_id != user.id]

    return direct_children, deeper_descendants
