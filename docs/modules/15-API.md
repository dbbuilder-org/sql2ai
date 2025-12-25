# SQL API

**Complete Data Layer Generation Platform**

## Overview

SQL API generates and maintains complete, type-safe data access layers from your database schema. It supports Python FastAPI, .NET Core, Next.js, and Node.js backends with typed clients for React, Vue, Next.js, and Python consumers. SQL API has native stored procedure integration with CRUD optimization and SAGA pattern handling for complex transactions.

## The Problem

### Current Data Layer Challenges

| Challenge | Traditional Approach | Pain Point |
|-----------|---------------------|------------|
| Manual API creation | Write by hand | Time-consuming, error-prone |
| Type safety | Manual type sync | Runtime errors, drift |
| Schema changes | Manual updates | API/DB out of sync |
| SP integration | Custom code | Inconsistent patterns |
| Transaction handling | Ad-hoc | No SAGA support |
| Documentation | Manual Swagger | Always outdated |

## SQL API Solution

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    DATABASE LAYER                                │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  Tables  │  Stored Procedures  │  Views  │  Functions      ││
│  └─────────────────────────────────────────────────────────────┘│
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SQL API ENGINE                                │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Schema Analysis → Code Generation → API Scaffolding       │ │
│  └────────────────────────────────────────────────────────────┘ │
└───────────────────────────┬─────────────────────────────────────┘
                            │
          ┌─────────────────┼─────────────────┐
          │                 │                 │
          ▼                 ▼                 ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│    FastAPI      │ │   .NET Core     │ │    Node.js      │
│    (Python)     │ │   (C#)          │ │   (TypeScript)  │
└────────┬────────┘ └────────┬────────┘ └────────┬────────┘
         │                   │                   │
         ▼                   ▼                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                    TYPE-SAFE CLIENTS                             │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌───────────┐ │
│  │   React     │ │    Vue      │ │   Next.js   │ │  Python   │ │
│  │   Client    │ │   Client    │ │   Client    │ │  Client   │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └───────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Backend Generation

### FastAPI (Python)

```python
# Generated: api/routers/customers.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime

from ..models import Customer, CustomerCreate, CustomerUpdate
from ..database import get_db

router = APIRouter(prefix="/customers", tags=["Customers"])

@router.get("/", response_model=List[Customer])
async def list_customers(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
) -> List[Customer]:
    """List all customers with optional filtering."""
    query = select(CustomerModel)
    if status:
        query = query.where(CustomerModel.status == status)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{customer_id}", response_model=Customer)
async def get_customer(
    customer_id: int,
    db: AsyncSession = Depends(get_db)
) -> Customer:
    """Get a specific customer by ID."""
    result = await db.execute(
        select(CustomerModel).where(CustomerModel.id == customer_id)
    )
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@router.post("/", response_model=Customer, status_code=201)
async def create_customer(
    customer: CustomerCreate,
    db: AsyncSession = Depends(get_db)
) -> Customer:
    """Create a new customer."""
    db_customer = CustomerModel(**customer.dict())
    db.add(db_customer)
    await db.commit()
    await db.refresh(db_customer)
    return db_customer

# Stored Procedure Integration
@router.post("/{customer_id}/orders", response_model=Order)
async def create_customer_order(
    customer_id: int,
    order: OrderCreate,
    db: AsyncSession = Depends(get_db)
) -> Order:
    """Create order via stored procedure with SAGA handling."""
    result = await db.execute(
        text("EXEC dbo.Order_CreateWithInventory :customer_id, :items"),
        {"customer_id": customer_id, "items": json.dumps(order.items)}
    )
    # SAGA: If inventory reservation fails, SP handles rollback
    return Order(**result.mappings().one())
```

### .NET Core (C#)

```csharp
// Generated: Controllers/CustomersController.cs
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace Api.Controllers;

[ApiController]
[Route("api/[controller]")]
public class CustomersController : ControllerBase
{
    private readonly AppDbContext _context;
    private readonly ICustomerRepository _repository;

    public CustomersController(AppDbContext context, ICustomerRepository repository)
    {
        _context = context;
        _repository = repository;
    }

    [HttpGet]
    public async Task<ActionResult<IEnumerable<CustomerDto>>> GetCustomers(
        [FromQuery] int skip = 0,
        [FromQuery] int limit = 100,
        [FromQuery] string? status = null)
    {
        var query = _context.Customers.AsQueryable();

        if (!string.IsNullOrEmpty(status))
            query = query.Where(c => c.Status == status);

        var customers = await query
            .Skip(skip)
            .Take(limit)
            .Select(c => new CustomerDto(c))
            .ToListAsync();

        return Ok(customers);
    }

    [HttpGet("{id}")]
    public async Task<ActionResult<CustomerDto>> GetCustomer(int id)
    {
        var customer = await _context.Customers.FindAsync(id);
        if (customer == null)
            return NotFound();
        return Ok(new CustomerDto(customer));
    }

    [HttpPost]
    public async Task<ActionResult<CustomerDto>> CreateCustomer(CustomerCreateDto dto)
    {
        var customer = new Customer
        {
            Name = dto.Name,
            Email = dto.Email,
            CreatedAt = DateTime.UtcNow
        };

        _context.Customers.Add(customer);
        await _context.SaveChangesAsync();

        return CreatedAtAction(nameof(GetCustomer), new { id = customer.Id },
            new CustomerDto(customer));
    }

    // Stored Procedure via Dapper
    [HttpPost("{id}/orders")]
    public async Task<ActionResult<OrderDto>> CreateOrder(
        int id,
        OrderCreateDto dto)
    {
        var result = await _repository.ExecuteOrderCreateWithInventoryAsync(
            id, dto.Items);
        return Ok(result);
    }
}
```

### Node.js (TypeScript)

```typescript
// Generated: src/routers/customers.ts
import { Router, Request, Response } from 'express';
import { z } from 'zod';
import { db } from '../database';
import { Customer, CustomerCreate } from '../types';

const router = Router();

// Validation schemas (auto-generated from DB)
const CustomerCreateSchema = z.object({
  name: z.string().max(100),
  email: z.string().email().max(255),
  status: z.enum(['Active', 'Inactive', 'Pending']).default('Pending'),
});

router.get('/', async (req: Request, res: Response) => {
  const { skip = 0, limit = 100, status } = req.query;

  let query = db('customers').select('*');
  if (status) query = query.where('status', status);

  const customers = await query.offset(Number(skip)).limit(Number(limit));
  res.json(customers);
});

router.get('/:id', async (req: Request, res: Response) => {
  const customer = await db('customers')
    .where('id', req.params.id)
    .first();

  if (!customer) {
    return res.status(404).json({ error: 'Customer not found' });
  }
  res.json(customer);
});

router.post('/', async (req: Request, res: Response) => {
  const validated = CustomerCreateSchema.parse(req.body);

  const [customer] = await db('customers')
    .insert(validated)
    .returning('*');

  res.status(201).json(customer);
});

// Stored Procedure call
router.post('/:id/orders', async (req: Request, res: Response) => {
  const result = await db.raw(
    'EXEC dbo.Order_CreateWithInventory ?, ?',
    [req.params.id, JSON.stringify(req.body.items)]
  );
  res.json(result[0]);
});

export default router;
```

## Type-Safe Client Generation

### React/TypeScript Client

```typescript
// Generated: src/api/client.ts
import { createApiClient } from '@sql2ai/client';
import type { Customer, CustomerCreate, Order, OrderCreate } from './types';

export const api = createApiClient({
  baseUrl: process.env.REACT_APP_API_URL,
});

// Type-safe API methods
export const customersApi = {
  list: (params?: { skip?: number; limit?: number; status?: string }) =>
    api.get<Customer[]>('/customers', { params }),

  get: (id: number) =>
    api.get<Customer>(`/customers/${id}`),

  create: (data: CustomerCreate) =>
    api.post<Customer>('/customers', data),

  update: (id: number, data: Partial<Customer>) =>
    api.patch<Customer>(`/customers/${id}`, data),

  delete: (id: number) =>
    api.delete(`/customers/${id}`),

  createOrder: (customerId: number, data: OrderCreate) =>
    api.post<Order>(`/customers/${customerId}/orders`, data),
};

// React Query hooks (auto-generated)
export const useCustomers = (params?: Parameters<typeof customersApi.list>[0]) =>
  useQuery(['customers', params], () => customersApi.list(params));

export const useCustomer = (id: number) =>
  useQuery(['customer', id], () => customersApi.get(id));

export const useCreateCustomer = () =>
  useMutation(customersApi.create, {
    onSuccess: () => queryClient.invalidateQueries(['customers']),
  });
```

### Vue Client

```typescript
// Generated: src/api/customers.ts
import { ref, computed } from 'vue';
import { useQuery, useMutation } from '@tanstack/vue-query';
import type { Customer, CustomerCreate } from './types';

export function useCustomers(params?: { status?: string }) {
  return useQuery({
    queryKey: ['customers', params],
    queryFn: () => fetch(`/api/customers?${new URLSearchParams(params)}`).then(r => r.json()),
  });
}

export function useCustomer(id: number) {
  return useQuery({
    queryKey: ['customer', id],
    queryFn: () => fetch(`/api/customers/${id}`).then(r => r.json()),
  });
}

export function useCreateCustomer() {
  return useMutation({
    mutationFn: (data: CustomerCreate) =>
      fetch('/api/customers', {
        method: 'POST',
        body: JSON.stringify(data),
      }).then(r => r.json()),
  });
}
```

## SAGA Pattern Support

For complex multi-step transactions:

```yaml
# saga-definitions.yaml
sagas:
  order_fulfillment:
    description: "Complete order with inventory, payment, and shipping"
    steps:
      - name: reserve_inventory
        procedure: dbo.Inventory_Reserve
        compensate: dbo.Inventory_Release

      - name: process_payment
        procedure: dbo.Payment_Process
        compensate: dbo.Payment_Refund

      - name: create_shipment
        procedure: dbo.Shipment_Create
        compensate: dbo.Shipment_Cancel

      - name: confirm_order
        procedure: dbo.Order_Confirm
        compensate: dbo.Order_Revert
```

**Generated SAGA Handler:**

```python
# Generated: api/sagas/order_fulfillment.py
class OrderFulfillmentSaga:
    async def execute(self, order_id: int, db: AsyncSession) -> SagaResult:
        completed_steps = []

        try:
            # Step 1: Reserve Inventory
            await db.execute(text("EXEC dbo.Inventory_Reserve :order_id"),
                           {"order_id": order_id})
            completed_steps.append("reserve_inventory")

            # Step 2: Process Payment
            await db.execute(text("EXEC dbo.Payment_Process :order_id"),
                           {"order_id": order_id})
            completed_steps.append("process_payment")

            # Step 3: Create Shipment
            await db.execute(text("EXEC dbo.Shipment_Create :order_id"),
                           {"order_id": order_id})
            completed_steps.append("create_shipment")

            # Step 4: Confirm Order
            await db.execute(text("EXEC dbo.Order_Confirm :order_id"),
                           {"order_id": order_id})

            await db.commit()
            return SagaResult(success=True)

        except Exception as e:
            # Compensate in reverse order
            for step in reversed(completed_steps):
                await self._compensate(step, order_id, db)
            await db.commit()
            return SagaResult(success=False, error=str(e))

    async def _compensate(self, step: str, order_id: int, db: AsyncSession):
        compensations = {
            "reserve_inventory": "dbo.Inventory_Release",
            "process_payment": "dbo.Payment_Refund",
            "create_shipment": "dbo.Shipment_Cancel",
        }
        if step in compensations:
            await db.execute(text(f"EXEC {compensations[step]} :order_id"),
                           {"order_id": order_id})
```

## API Operations Configuration

```json
// api-operations.json
{
  "customers": {
    "endpoints": {
      "list": { "method": "GET", "path": "/", "paginated": true },
      "get": { "method": "GET", "path": "/:id" },
      "create": { "method": "POST", "path": "/" },
      "update": { "method": "PATCH", "path": "/:id" },
      "delete": { "method": "DELETE", "path": "/:id" }
    },
    "procedures": {
      "getOrders": {
        "sp": "dbo.Customer_GetOrders",
        "method": "GET",
        "path": "/:id/orders"
      },
      "createOrder": {
        "saga": "order_fulfillment",
        "method": "POST",
        "path": "/:id/orders"
      }
    }
  }
}
```

## Schema Sync

When database schema changes, SQL API detects and updates:

```
╔══════════════════════════════════════════════════════════════════╗
║              SQL API SCHEMA SYNC                                 ║
╠══════════════════════════════════════════════════════════════════╣
║ DETECTED CHANGES                                                 ║
║ ─────────────────────────────────────────────────────────────── ║
║ + Customers.LoyaltyTier (new column, VARCHAR(20))               ║
║ ~ Orders.Status (added value: 'PartiallyShipped')               ║
║ + dbo.Customer_GetLoyaltyHistory (new procedure)                ║
║ - dbo.Legacy_GetCustomer (removed procedure)                    ║
╠══════════════════════════════════════════════════════════════════╣
║ GENERATED UPDATES                                                ║
║ ─────────────────────────────────────────────────────────────── ║
║ ✓ Updated CustomerDto with LoyaltyTier field                    ║
║ ✓ Updated OrderStatus enum                                       ║
║ ✓ Generated getLoyaltyHistory endpoint                          ║
║ ✓ Removed legacyGetCustomer endpoint                            ║
║ ✓ Regenerated TypeScript client types                           ║
╚══════════════════════════════════════════════════════════════════╝
```

## CLI Commands

```bash
# Initialize API project
sql2ai api init --backend fastapi --database "..."

# Generate/update API from schema
sql2ai api generate

# Generate client SDKs
sql2ai api client --framework react --output ./client

# Sync with database changes
sql2ai api sync

# Generate OpenAPI spec
sql2ai api openapi --output api-spec.yaml
```

## Integration Points

- **SQL Migrator**: Regenerate API when migrations run
- **SQL Code**: Data dictionary provides endpoint descriptions
- **SQL Test**: Generate API integration tests
- **SQL Standardize**: Enforce API naming conventions
