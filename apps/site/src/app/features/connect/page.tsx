import { Metadata } from 'next';
import Link from 'next/link';
import { CTASection } from '../../../components/marketing';

export const metadata: Metadata = {
  title: 'SQL Connect - Complete Data Layer Generation | SQL2.AI',
  description:
    'Generate type-safe APIs from your database schema. FastAPI, .NET Core, Node.js with SAGA pattern support and automatic maintenance.',
};

export default function APIPage(): JSX.Element {
  return (
    <>
      {/* Hero */}
      <section className="pt-32 pb-16 md:pt-40 md:pb-20">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto">
            <Link
              href="/features/"
              className="inline-flex items-center gap-2 text-small text-text-muted hover:text-text-secondary mb-6"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              All Modules
            </Link>

            <div className="flex items-center gap-4 mb-6">
              <div className="w-16 h-16 rounded-2xl bg-[#6366F1]/10 flex items-center justify-center text-[#6366F1]">
                <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
              <div>
                <h1 className="text-h1 text-text-primary">SQL Connect</h1>
                <p className="text-lg text-[#6366F1] font-medium">Data Layer Generation</p>
              </div>
            </div>

            <p className="text-xl text-text-secondary mb-8">
              Generate complete, type-safe data layers from your database schema. FastAPI, .NET Core,
              Node.js, and Next.js with SAGA pattern support for distributed transactions.
            </p>
          </div>
        </div>
      </section>

      {/* Framework Support */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <h2 className="text-h2 text-text-primary mb-12 text-center">Supported Frameworks</h2>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-5xl mx-auto">
            {[
              { name: 'FastAPI', icon: '🐍', desc: 'Python async API with Pydantic models' },
              { name: '.NET Core', icon: '💜', desc: 'C# Web API with Entity Framework' },
              { name: 'Node.js', icon: '💚', desc: 'Express/Fastify with TypeScript' },
              { name: 'Next.js', icon: '▲', desc: 'API routes with tRPC support' },
            ].map((fw) => (
              <div key={fw.name} className="card p-6 text-center">
                <div className="text-3xl mb-3">{fw.icon}</div>
                <h3 className="text-h5 text-text-primary mb-2">{fw.name}</h3>
                <p className="text-sm text-text-muted">{fw.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* What Gets Generated */}
      <section className="section">
        <div className="container-wide">
          <h2 className="text-h2 text-text-primary mb-12 text-center">Generated Components</h2>

          <div className="grid md:grid-cols-2 gap-8 max-w-5xl mx-auto">
            <div className="card p-6">
              <h3 className="text-h5 text-text-primary mb-4">API Layer</h3>
              <ul className="space-y-2 text-text-secondary text-sm">
                <li className="flex items-center gap-2">
                  <svg className="w-4 h-4 text-[#6366F1]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  RESTful endpoints for all tables
                </li>
                <li className="flex items-center gap-2">
                  <svg className="w-4 h-4 text-[#6366F1]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Stored procedure endpoints
                </li>
                <li className="flex items-center gap-2">
                  <svg className="w-4 h-4 text-[#6366F1]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  OpenAPI/Swagger documentation
                </li>
                <li className="flex items-center gap-2">
                  <svg className="w-4 h-4 text-[#6366F1]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Authentication middleware
                </li>
              </ul>
            </div>

            <div className="card p-6">
              <h3 className="text-h5 text-text-primary mb-4">Type Definitions</h3>
              <ul className="space-y-2 text-text-secondary text-sm">
                <li className="flex items-center gap-2">
                  <svg className="w-4 h-4 text-[#6366F1]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  TypeScript interfaces
                </li>
                <li className="flex items-center gap-2">
                  <svg className="w-4 h-4 text-[#6366F1]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Zod validation schemas
                </li>
                <li className="flex items-center gap-2">
                  <svg className="w-4 h-4 text-[#6366F1]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Pydantic models (Python)
                </li>
                <li className="flex items-center gap-2">
                  <svg className="w-4 h-4 text-[#6366F1]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  C# DTOs and records
                </li>
              </ul>
            </div>

            <div className="card p-6">
              <h3 className="text-h5 text-text-primary mb-4">Frontend Clients</h3>
              <ul className="space-y-2 text-text-secondary text-sm">
                <li className="flex items-center gap-2">
                  <svg className="w-4 h-4 text-[#6366F1]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  React Query hooks
                </li>
                <li className="flex items-center gap-2">
                  <svg className="w-4 h-4 text-[#6366F1]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Vue composables
                </li>
                <li className="flex items-center gap-2">
                  <svg className="w-4 h-4 text-[#6366F1]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Python SDK client
                </li>
                <li className="flex items-center gap-2">
                  <svg className="w-4 h-4 text-[#6366F1]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  tRPC client/server
                </li>
              </ul>
            </div>

            <div className="card p-6">
              <h3 className="text-h5 text-text-primary mb-4">SAGA Support</h3>
              <ul className="space-y-2 text-text-secondary text-sm">
                <li className="flex items-center gap-2">
                  <svg className="w-4 h-4 text-[#6366F1]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Distributed transaction handling
                </li>
                <li className="flex items-center gap-2">
                  <svg className="w-4 h-4 text-[#6366F1]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Compensation logic
                </li>
                <li className="flex items-center gap-2">
                  <svg className="w-4 h-4 text-[#6366F1]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  State machine tracking
                </li>
                <li className="flex items-center gap-2">
                  <svg className="w-4 h-4 text-[#6366F1]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Retry and rollback
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Sample Generated Code */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-h2 text-text-primary mb-8 text-center">Sample Generated Code</h2>

            <div className="card p-6">
              <pre className="bg-bg-primary rounded-lg p-4 text-sm overflow-x-auto">
                <code className="text-text-secondary">{`# Generated FastAPI endpoint
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

router = APIRouter(prefix="/customers", tags=["customers"])

class Customer(BaseModel):
    customer_id: int
    first_name: str
    last_name: str
    email: str
    created_at: datetime

class CustomerCreate(BaseModel):
    first_name: str
    last_name: str
    email: str

@router.get("/", response_model=List[Customer])
async def list_customers(
    skip: int = 0,
    limit: int = 100,
    db: Database = Depends(get_db)
):
    """List all customers with pagination."""
    return await db.fetch_all(
        "SELECT * FROM Customers ORDER BY customer_id OFFSET :skip ROWS FETCH NEXT :limit ROWS ONLY",
        {"skip": skip, "limit": limit}
    )

@router.post("/", response_model=Customer)
async def create_customer(
    customer: CustomerCreate,
    db: Database = Depends(get_db)
):
    """Create a new customer."""
    result = await db.execute(
        "EXEC dbo.CreateCustomer @FirstName=:first_name, @LastName=:last_name, @Email=:email",
        customer.dict()
    )
    return await db.fetch_one("SELECT * FROM Customers WHERE customer_id = :id", {"id": result})`}</code>
              </pre>
            </div>
          </div>
        </div>
      </section>

      {/* API Operations Config */}
      <section className="section">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-h2 text-text-primary mb-4 text-center">Configuration-Driven</h2>
            <p className="text-text-secondary text-center mb-12">
              Define your API structure in JSON or use the database table for dynamic operations
            </p>

            <div className="card p-6">
              <pre className="bg-bg-primary rounded-lg p-4 text-sm overflow-x-auto">
                <code className="text-text-secondary">{`{
  "api_operations": [
    {
      "name": "GetCustomerOrders",
      "method": "GET",
      "path": "/customers/{customerId}/orders",
      "procedure": "dbo.GetCustomerOrders",
      "parameters": [
        {"name": "customerId", "type": "int", "source": "path"}
      ],
      "response": {
        "type": "array",
        "schema": "Order"
      }
    },
    {
      "name": "ProcessPayment",
      "method": "POST",
      "path": "/payments",
      "saga": {
        "enabled": true,
        "steps": [
          {"action": "ValidatePayment", "compensation": "VoidPayment"},
          {"action": "DeductInventory", "compensation": "RestoreInventory"},
          {"action": "CreateShipment", "compensation": "CancelShipment"}
        ]
      }
    }
  ]
}`}</code>
              </pre>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <CTASection
        title="Generate Your API Layer"
        description="Type-safe APIs with SAGA pattern support, generated and maintained automatically."
        primaryCTA={{ text: 'Start Free Trial', href: '/signup' }}
        secondaryCTA={{ text: 'View All Features', href: '/features/' }}
      />
    </>
  );
}
