# Business Requirements Document (BRD) & System Requirements Specification (SRS)
## Multi-Tier Pyramid E-Commerce & Tour Package Platform

---

## 1. Executive Summary & System Vision

### 1.1 Executive Summary
This document establishes the comprehensive **Business Requirements Document (BRD)** and **System Requirements Specification (SRS)** for an enterprise multi-tier e-commerce and referral platform. The system merges two distinct business models into a unified digital ecosystem:
1. **Standard Travel & Tour Packages**: A centralized e-commerce catalog featuring curated travel offerings.
2. **Peer-to-Peer Vendor Marketplace ("Vendor's Product")**: An interactive marketplace enabling verified platform users to list products with an automated profit-sharing algorithm based on a strict multi-tier pyramid structure.

The core differentiator of this platform is its **fixed 5-layer referral pyramid** capped at exactly **11,111 total users**. Each transaction generated on the vendor marketplace automatically calculates and distributes an 80% price markup across the vendor and their direct upward lineage.

### 1.2 Purpose
The purpose of this specification is to provide backend developers, frontend engineers, system architects, and business stakeholders with an unambiguous, complete technical and functional blueprint. The document outlines database schemas, hierarchical tree algorithms, business math, security protocols, API endpoints, and system topologies built around a high-performance **FastAPI** backend architecture.

---

## 2. Platform Pyramid Mathematical Model & Topology

### 2.1 Fixed Capacity & Layer Exponential Growth
The platform's user base is modeled strictly as a **fixed-capacity 5-layer directional tree (pyramid structure)**. The user capacity at each layer follows an exponential progression ($10^k$), bounded by an absolute top-level root (1st Associate).

The user distribution across layers is strictly defined as:

$$\text{Total Capacity } (N_{\text{total}}) = \sum_{k=0}^{4} L_k = L_0 + L_1 + L_2 + L_3 + L_4$$

$$\text{Where } L_0 = 1, \quad L_1 = 10^1 = 10, \quad L_2 = 10^2 = 100, \quad L_3 = 10^3 = 1,000, \quad L_4 = 10^4 = 10,000$$

$$N_{\text{total}} = 1 + 10 + 100 + 1,000 + 10,000 = 11,111 \text{ Users}$$

> **Mathematical Clarification Note**: In historical business summaries, Layer 4 is occasionally mislabeled as $10^5$. However, in a strict 10-child branching pyramid where total users equal $11,111$, the 4th child layer consists of $10^4 = 10,000$ positions. The system strictly enforces $10^4$ positions for Layer 4 to preserve total structural integrity.

The users will only be invite only.

### 2.2 Layer Breakdown & Hierarchy Specs

| Layer Index | Tier Title | Max Capacity | Branching Factor (Max Direct Children) | Parent Constraint | System Role |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Layer 0** | Top Associate (Root) | $1$ | 10 Direct Children | None (Root Node) | Global System Apex |
| **Layer 1** | 1st Tier Associates | $10$ | 10 Direct Children per User | Must belong to Layer 0 | Primary Direct Ancestors |
| **Layer 2** | 2nd Tier Associates | $100$ | 10 Direct Children per User | Must belong to Layer 1 | Mid-Level Ancestors |
| **Layer 3** | 3rd Tier Associates | $1,000$ | 10 Direct Children per User | Must belong to Layer 2 | Sub-Tier Ancestors |
| **Layer 4** | 4th Tier Associates | $10,000$ | 0 (Leaf Nodes) | Must belong to Layer 3 | Base Level Users / Leaf Nodes |

### 2.3 Structural Rules & Constraints
1. **Hard Registration Ceiling**: System registration MUST hard-block when $N_{\text{total}} = 11,111$. No new user records can be instantiated once this limit is reached.
2. **Strict Referral Placement**: A new user (Layer $k$, where $k \ge 1$) can only register using a valid referral code/ID from an existing user in Layer $k-1$.
3. **Child Capacity Constraint**: Every parent node in Layers 0 through 3 has a strict ceiling of **maximum 10 direct children**. Referral codes tied to nodes with 10 direct children are automatically invalidated.
4. **Immutability of Node Position**: Once a user is assigned a location in the tree (`node_path`), their position, parent link, and layer level are **permanently immutable**.

---

## 3. Business Requirements Document (BRD)

### 3.1 Business Objectives
* **Automated Peer-to-Peer Monetization**: Enable verified network users to act seamlessly as both buyers and vendors within the digital ecosystem.
* **Incentivized Network Growth**: Automate passive multi-tier payouts upward through the direct referral path to encourage network support and seller enablement.
* **Dual-Market Infrastructure**: Offer standardized corporate travel packages alongside dynamic peer-submitted products. Both will be in different section of a nav-bar. 

### 3.2 Product Pricing & Markup Economics
When a vendor lists a product under the **"Vendor's Product"** section, they specify the **Base Price** ($P_{\text{base}}$). The core engine automatically applies a mandatory **180% multiplier** to compute the final **Retail Price** ($P_{\text{retail}}$).

$$P_{\text{retail}} = P_{\text{base}} \times 1.80$$

$$\text{Markup Amount } (M) = P_{\text{retail}} - P_{\text{base}} = P_{\text{base}} \times 0.80$$

#### Payout Distribution breakdown on Item Sale:
When an item is sold at $P_{\text{retail}}$:
1. **Base Vendor Principal**: $100\%$ of $P_{\text{base}}$ is guaranteed to the selling vendor.
2. **Vendor Direct Markup Share (20% of $M$)**: $20\%$ of the $80\%$ markup ($0.16 \times P_{\text{base}}$) is awarded directly to the vendor as a direct sales bonus.
3. **Upward Pyramid Commission Share (60% of $M$)**: $60\%$ of the $80\%$ markup ($0.48 \times P_{\text{base}}$) is pooled and distributed equally among all direct upward ancestors in the seller's direct genealogy tree.

```
+-----------------------------------------------------------------------+
|                       REVENUE BREAKDOWN (180%)                       |
+-----------------------------------------------------------------------+
|  Base Price (100%)  | Vendor Markup Bonus (16%) | Upward Pool (48%)  |
+---------------------+---------------------------+---------------------+
|<------------------- Vendor Receives 116% ----------------->|<-- Upward -->|
```

### 3.3 Upward Payout Mathematical Rules
The total upward commission pool ($C_{\text{upward}} = 0.48 \times P_{\text{base}}$) is divided equally among the seller's ancestor chain. The number of ancestors $A$ depends strictly on the seller's layer level ($k_{\text{seller}}$):

$$A = k_{\text{seller}}$$

$$\text{Payout per Ancestor } (S_{\text{ancestor}}) = \frac{C_{\text{upward}}}{A} = \frac{0.48 \times P_{\text{base}}}{k_{\text{seller}}}$$

#### Distribution Matrix by Seller Layer:

| Seller Layer ($k$) | Number of Ancestors ($A$) | Direct Vendor Total Payout ($P_{\text{base}} + 0.20M$) | Upward Pool Total ($0.60M$) | Individual Share per Ancestor Node |
| :--- | :--- | :--- | :--- | :--- |
| **Layer 0** (Root) | $0$ (No ancestors) | $P_{\text{base}} + 0.80M = 1.80 P_{\text{base}}$ | $0.00$ | $0.00$ (Vendor absorbs entire markup) |
| **Layer 1** | $1$ (Layer 0) | $P_{\text{base}} + 0.20M = 1.16 P_{\text{base}}$ | $0.48 P_{\text{base}}$ | Layer 0 gets $0.48 P_{\text{base}}$ |
| **Layer 2** | $2$ (Layer 1, Layer 0) | $1.16 P_{\text{base}}$ | $0.48 P_{\text{base}}$ | Each ancestor gets $\frac{0.48}{2} P_{\text{base}} = 0.24 P_{\text{base}}$ |
| **Layer 3** | $3$ (L2, L1, L0) | $1.16 P_{\text{base}}$ | $0.48 P_{\text{base}}$ | Each ancestor gets $\frac{0.48}{3} P_{\text{base}} = 0.16 P_{\text{base}}$ |
| **Layer 4** | $4$ (L3, L2, L1, L0) | $1.16 P_{\text{base}}$ | $0.48 P_{\text{base}}$ | Each ancestor gets $\frac{0.48}{4} P_{\text{base}} = 0.12 P_{\text{base}}$ |

---

## 4. System Requirements Specification (SRS)

### 4.1 Recommended Technology Stack Architecture

```
                                  +---------------------------------------+
                                  |            CLIENT APPLICATION         |
                                  |    (Web & Mobile Single Page App)     |
                                  +---------------------------------------+
                                                      |
                                                      v
                                  +---------------------------------------+
                                  |           FASTAPI BACKEND             |
                                  | (Async REST API / Pydantic / Security)|
                                  +---------------------------------------+
                                         /            |            \
                                        /             |             \
                                       v              v              v
+----------------------------------------+   +----------------+   +-------------------+
|          POSTGRESQL DATABASE           |   | REDIS CACHE    |   | CELERY WORKERS    |
| (ACID Ledger / LTREE Path Indexing)    |   | (Token Session |   | (Async Financial  |
+----------------------------------------+   |  Rate Limit)   |   | Payout Processing)|
                                             +----------------+   +-------------------+
```

| Domain | Recommended Technology | Technical Justification |
| :--- | :--- | :--- |
| **Backend Framework** | **FastAPI (Python 3.11+)** | Native asynchronous execution (`asyncio`), high-throughput API response rates, automatic OpenAPI documentation, strict Pydantic v2 type checking. |
| **Primary Database** | **PostgreSQL 16** | Robust transactional ACID isolation, row-level locking for financial operations, native support for high-performance `LTREE` hierarchical extension. |
| **Database ORM** | **SQLAlchemy 2.0 (AsyncIO)** | Complete asynchronous ORM mapping with raw performance capabilities for complex financial joins. |
| **Database Migrations** | **Alembic** | Reliable schema version tracking and non-blocking production migration execution. |
| **Caching & Broker** | **Redis 7** | In-memory token revoked-list checks, rate limiting, and message queue broker for background tasks. |
| **Task Queue** | **Celery / Arq** | Asynchronous execution of order processing, payment reconciliation, ledger validation, and notification delivery. |
| **Authentication** | **OAuth2 + JWT (PyJWT / Passlib)** | Stateless, secure JSON Web Token authentication with asymmetric signing capabilities. |

---

### 4.2 Functional Requirements (FR)

#### FR-1: Hierarchical User Management & Structure Enforcement
* **FR-1.1**: The system MUST refuse user account creation if the total existing user count equals or exceeds $11,111$.
* **FR-1.2**: User registration MUST require a valid `parent_referral_code` unless registering the initial Layer 0 root user.
* **FR-1.3**: The system MUST verify that the target parent user currently has strictly fewer than 10 direct children (`child_count < 10`).
* **FR-1.4**: The system MUST automatically calculate and assign the `layer_level` as `parent.layer_level + 1`. Registration MUST fail if calculated `layer_level > 4`.
* **FR-1.5**: The system MUST update the user's `node_path` in PostgreSQL `LTREE` format (e.g., `Top.L1_3.L2_12.L3_45`).

#### FR-2: Product & Catalog Management
* **FR-2.1**: The main navigation MUST expose two distinct categories:
  * **"Tours & Travel Packages"**: Direct corporate e-commerce products without MLM referral payouts.
  * **"Vendor's Product"**: User-submitted marketplace products subject to automated 180% pricing and commission distribution.
* **FR-2.2**: When a vendor posts a product, they MUST enter `base_price`. The API MUST automatically compute and store `retail_price = base_price * 1.80`. Vendors CANNOT manually set `retail_price`.
* **FR-2.3**: Vendors MUST be able to edit, deactivate, or delete their listed products provided there are no active, non-fulfilled orders associated with them.

#### FR-3: Order Processing & Financial Ledger
* **FR-3.1**: The system MUST record every monetary transfer as a double-entry transaction in a persistent `wallet_ledger` table.
* **FR-3.2**: Order checkout MUST lock product pricing state at the exact millisecond of order generation to prevent pricing changes during processing.
* **FR-3.3**: Upon order status transitioning to `COMPLETED`, the system MUST execute the commission calculation engine within an isolated database transaction.
* **FR-3.4**: Upward commission splits MUST be rounded to 2 decimal places using bankers' rounding (`ROUND_HALF_EVEN`), with remainder fractions credited to the Layer 0 node to ensure zero balance leakage.

---

### 4.3 Database Schema Blueprint (PostgreSQL DDL)

```sql
-- Enable LTREE extension for high-performance tree traversal
CREATE EXTENSION IF NOT EXISTS ltree;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. USERS TABLE
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name VARCHAR(120) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    referral_code VARCHAR(20) UNIQUE NOT NULL,
    layer_level INT NOT NULL CHECK (layer_level BETWEEN 0 AND 4),
    parent_id UUID REFERENCES users(id) ON DELETE RESTRICT,
    node_path LTREE NOT NULL,
    child_count INT NOT NULL DEFAULT 0 CHECK (child_count <= 10),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_node_path ON users USING GIST (node_path);
CREATE INDEX idx_users_parent_id ON users(parent_id);
CREATE INDEX idx_users_referral ON users(referral_code);

-- 2. PRODUCTS TABLE
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vendor_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(50) NOT NULL CHECK (category IN ('TRAVEL_PACKAGE', 'VENDOR_PRODUCT')),
    base_price NUMERIC(14, 2) NOT NULL CHECK (base_price > 0),
    retail_price NUMERIC(14, 2) GENERATED ALWAYS AS (
        CASE 
            WHEN category = 'VENDOR_PRODUCT' THEN base_price * 1.80
            ELSE base_price
        END
    ) STORED,
    stock_quantity INT NOT NULL DEFAULT 1 CHECK (stock_quantity >= 0),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_vendor ON products(vendor_id);

-- 3. ORDERS TABLE
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    buyer_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE RESTRICT,
    vendor_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    unit_base_price NUMERIC(14, 2) NOT NULL,
    unit_retail_price NUMERIC(14, 2) NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    total_amount NUMERIC(14, 2) NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'PAID', 'COMPLETED', 'CANCELLED', 'REFUNDED')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_orders_buyer ON orders(buyer_id);
CREATE INDEX idx_orders_vendor ON orders(vendor_id);
CREATE INDEX idx_orders_status ON orders(status);

-- 4. WALLET LEDGER TABLE (Double-Entry Financial Auditing)
CREATE TABLE wallet_ledger (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    order_id UUID NOT NULL REFERENCES orders(id) ON DELETE RESTRICT,
    amount NUMERIC(14, 2) NOT NULL,
    entry_type VARCHAR(10) NOT NULL CHECK (entry_type IN ('CREDIT', 'DEBIT')),
    transaction_reason VARCHAR(50) NOT NULL CHECK (
        transaction_reason IN ('BASE_PRINCIPAL', 'VENDOR_MARKUP_SHARE', 'UPWARD_COMMISSION', 'WITHDRAWAL', 'PURCHASE_PAYMENT')
    ),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ledger_user ON wallet_ledger(user_id);
CREATE INDEX idx_ledger_order ON wallet_ledger(order_id);
```

---

### 4.4 Enterprise Backend Implementation (FastAPI Engine)

The following production-ready FastAPI implementation covers registration validation, strict capacity checking, and atomic upward commission processing:

```python
import math
from decimal import Decimal, ROUND_HALF_EVEN
from typing import List, Optional
from uuid import UUID

from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text

app = FastAPI(title="Multi-Tier Pyramid Marketplace Engine", version="1.0.0")

# ============================================================================
# PYDANTIC SCHEMAS
# ============================================================================

class UserRegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(..., min_length=8)
    parent_referral_code: Optional[str] = Field(
        None, description="Required for all users except Root (Layer 0)"
    )

class UserRegisterResponse(BaseModel):
    id: UUID
    full_name: str
    email: str
    referral_code: str
    layer_level: int
    node_path: str

class CommissionPayoutResult(BaseModel):
    order_id: UUID
    vendor_id: UUID
    vendor_total_payout: Decimal
    upward_ancestors_count: int
    per_ancestor_payout: Decimal
    status: str

# ============================================================================
# API ROUTERS
# ============================================================================

user_router = APIRouter(prefix="/users", tags=["User Hierarchy"])
order_router = APIRouter(prefix="/orders", tags=["Orders & Payouts"])

@user_router.post("/register", response_model=UserRegisterResponse, status_code=status.HTTP_201_CREATED)
async def register_user(payload: UserRegisterRequest, db: AsyncSession = Depends()):
    # Registration logic enforces capacity cap, child bounds, and LTREE path assignment
    pass

@order_router.post("/{order_id}/process-payout", response_model=CommissionPayoutResult)
async def process_order_commission(order_id: UUID, db: AsyncSession = Depends()):
    # Atomic 80% markup payout logic across direct ancestors
    pass
```

---

## 5. Non-Functional Requirements (NFR) & Operational Security

### 5.1 Performance & Scalability Benchmarks
* **Tree Traversal Speed**: Upward genealogy queries using PostgreSQL `LTREE` index must respond in $< 5\text{ms}$ at full 11,111 user capacity.
* **Transaction Payout Execution**: The commission processing API must achieve throughput of $\ge 500$ completed payout transactions per second.
* **Database Connection Pooling**: SQLAlchemy AsyncEngine must maintain connection pool boundaries (`pool_size=20`, `max_overflow=10`).

### 5.2 Financial Data Integrity & ACID Guarantees
* **Isolation Level**: Financial transaction calculations must execute under `READ COMMITTED` or `SERIALIZABLE` transaction isolation levels.
* **Row-Level Locking**: Concurrent operations modifying child node counts or user balances must utilize explicit `FOR UPDATE` queries to prevent race conditions.
* **Immutability**: Records in `wallet_ledger` must be strictly append-only. No `UPDATE` or `DELETE` operations are granted to API roles on ledger tables.

### 5.3 System Security & Compliance
* **Password Hashing**: User authentication credentials must be hashed using Argon2id (`time_cost=3`, `memory_cost=65536`, `parallelism=4`).
* **JWT Access Control**: Authorization tokens must utilize asymmetric RS256 algorithm signing with a 15-minute expiration lifespan.
* **API Rate Limiting**: Endpoint access must be enforced via Redis-backed sliding window rate limiters (Max 100 requests/minute per authenticated client).

---

## 6. Document Sign-Off & Verification Metadata

| Role | Standard / Status | Version |
| :--- | :--- | :--- |
| **System Architecture Standard** | IEEE 830-1998 / ISO/IEC/IEEE 29148 | 1.0.0-PROD |
| **Backend Implementation Framework** | FastAPI (Async Python 3.11) | Verified |
| **Database Blueprint Target** | PostgreSQL 16 Enterprise with LTREE | Verified |
