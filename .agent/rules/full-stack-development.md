---
trigger: always_on
---

# Full-Stack Development Rule

> [!IMPORTANT]
> All changes in this project are **full-stack changes**. Every feature, update, or modification must be implemented across all layers of the application.

## Required Layers for Every Change

When implementing any feature or modification, you MUST ensure the change is reflected in:

### 1. **Frontend** (Next.js/React)
- UI components and pages
- Form validation schemas (Zod)
- Type definitions
- State management
- API client calls

### 2. **API** (Django REST Framework)
- API endpoints and views
- Serializers (request/response)
- URL routing
- Permissions and authentication

### 3. **Database** (PostgreSQL via Supabase/Django ORM)
- Model definitions
- Migrations
- Field constraints and validations

---

## Verification Checklist

Before considering any feature complete, verify:

- [ ] **Frontend displays the new field/feature correctly**
- [ ] **Frontend validation works (Zod schema updated)**
- [ ] **API accepts and processes the data correctly**
- [ ] **API serializer includes the new field**
- [ ] **Database migration is created and can be applied**
- [ ] **End-to-end flow works: UI -> API -> Database -> API -> UI**

---

## Example: Adding a New Field

If adding a field like `pacing` to novels:

1. **Database**: Add field to Django model, create migration
2. **API**: Update serializer to include the field
3. **Frontend**: 
   - Add to TypeScript types
   - Add to Zod validation schema
   - Add UI input component
   - Update form submission handler

Never implement a change in isolation on just one layer.
