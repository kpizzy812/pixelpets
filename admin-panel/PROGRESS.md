# Admin Panel Development Progress

## Overview
Building a modern admin panel for Pixel Pets using Next.js 15, shadcn/ui, TanStack Query, and Zustand.

## Tech Stack
- **Framework**: Next.js 15 (App Router)
- **UI Library**: shadcn/ui + Tailwind CSS v4
- **State Management**: Zustand (auth state)
- **Data Fetching**: TanStack Query v5
- **Icons**: Lucide React
- **Form Validation**: React Hook Form + Zod

## API Endpoints Summary
The backend provides these admin endpoints (all require JWT auth):

### Authentication
- `POST /admin/login` - Login with username/password
- `GET /admin/me` - Get current admin profile
- `POST /admin/admins` - Create new admin (SUPER_ADMIN only)
- `PATCH /admin/admins/{id}` - Update admin (SUPER_ADMIN only)

### Dashboard
- `GET /admin/stats/dashboard` - Get dashboard statistics

### Users Management
- `GET /admin/users` - List users with pagination/search
- `GET /admin/users/{id}` - Get user details
- `POST /admin/users/{id}/balance` - Adjust user balance

### Deposits
- `GET /admin/deposits` - List deposit requests
- `POST /admin/deposits/{id}/action` - Approve/Reject deposit

### Withdrawals
- `GET /admin/withdrawals` - List withdrawal requests
- `POST /admin/withdrawals/{id}/action` - Complete/Reject withdrawal

### Pet Types
- `GET /admin/pet-types` - List pet types
- `POST /admin/pet-types` - Create pet type
- `PATCH /admin/pet-types/{id}` - Update pet type
- `DELETE /admin/pet-types/{id}` - Delete pet type

### Tasks
- `GET /admin/tasks` - List tasks
- `POST /admin/tasks` - Create task
- `PATCH /admin/tasks/{id}` - Update task
- `DELETE /admin/tasks/{id}` - Delete task

### Config
- `GET /admin/config` - Get all configs
- `GET /admin/config/referrals` - Get referral config
- `PUT /admin/config/referrals` - Update referral config
- `PUT /admin/config/{key}` - Update single config

### Audit Logs
- `GET /admin/logs` - View admin action logs (SUPER_ADMIN only)

## Admin Roles
- **SUPER_ADMIN**: Full access, manage admins, view logs
- **ADMIN**: Manage users, deposits, withdrawals, pet types, tasks
- **MODERATOR**: View-only access

---

## Progress

### Phase 1: Project Setup [IN PROGRESS]
- [x] Create project structure
- [ ] Install dependencies (Next.js, shadcn/ui, TanStack Query, etc.)
- [ ] Configure Tailwind CSS v4
- [ ] Setup environment variables
- [ ] Create base layout with sidebar

### Phase 2: Authentication [PENDING]
- [ ] Create login page
- [ ] Setup auth store (Zustand)
- [ ] Create API client with interceptors
- [ ] Implement protected routes middleware
- [ ] Add logout functionality

### Phase 3: Dashboard [PENDING]
- [ ] Create dashboard page
- [ ] Implement stats cards
- [ ] Add recent activity widgets

### Phase 4: Users Management [PENDING]
- [ ] Users list with search/pagination
- [ ] User detail page
- [ ] Balance adjustment modal

### Phase 5: Financial Management [PENDING]
- [ ] Deposits list with filters
- [ ] Deposit approval/rejection
- [ ] Withdrawals list with filters
- [ ] Withdrawal completion/rejection

### Phase 6: Content Management [PENDING]
- [ ] Pet types CRUD
- [ ] Tasks CRUD

### Phase 7: Settings & Logs [PENDING]
- [ ] System config page
- [ ] Referral config
- [ ] Admin logs viewer (SUPER_ADMIN)

---

## File Structure
```
admin-panel/
├── app/
│   ├── (auth)/
│   │   └── login/
│   │       └── page.tsx
│   ├── (dashboard)/
│   │   ├── layout.tsx           # Dashboard layout with sidebar
│   │   ├── page.tsx             # Dashboard home
│   │   ├── users/
│   │   │   ├── page.tsx         # Users list
│   │   │   └── [id]/page.tsx    # User detail
│   │   ├── deposits/
│   │   │   └── page.tsx
│   │   ├── withdrawals/
│   │   │   └── page.tsx
│   │   ├── pet-types/
│   │   │   └── page.tsx
│   │   ├── tasks/
│   │   │   └── page.tsx
│   │   ├── config/
│   │   │   └── page.tsx
│   │   └── logs/
│   │       └── page.tsx
│   ├── layout.tsx
│   └── globals.css
├── components/
│   ├── ui/                      # shadcn/ui components
│   ├── layout/
│   │   ├── sidebar.tsx
│   │   ├── header.tsx
│   │   └── nav-links.tsx
│   ├── users/
│   │   ├── users-table.tsx
│   │   ├── user-detail-card.tsx
│   │   └── balance-adjust-modal.tsx
│   ├── deposits/
│   │   ├── deposits-table.tsx
│   │   └── deposit-action-modal.tsx
│   ├── withdrawals/
│   │   ├── withdrawals-table.tsx
│   │   └── withdrawal-action-modal.tsx
│   ├── pet-types/
│   │   ├── pet-types-table.tsx
│   │   └── pet-type-form.tsx
│   ├── tasks/
│   │   ├── tasks-table.tsx
│   │   └── task-form.tsx
│   └── shared/
│       ├── data-table.tsx
│       ├── pagination.tsx
│       ├── status-badge.tsx
│       └── confirm-dialog.tsx
├── lib/
│   ├── api/
│   │   ├── client.ts            # Axios instance with interceptors
│   │   ├── auth.ts              # Auth API calls
│   │   ├── users.ts             # Users API calls
│   │   ├── deposits.ts
│   │   ├── withdrawals.ts
│   │   ├── pet-types.ts
│   │   ├── tasks.ts
│   │   ├── config.ts
│   │   ├── stats.ts
│   │   └── logs.ts
│   ├── hooks/
│   │   ├── use-auth.ts
│   │   ├── use-users.ts
│   │   ├── use-deposits.ts
│   │   └── ... (query hooks)
│   └── utils.ts
├── store/
│   └── auth-store.ts
├── types/
│   ├── api.ts                   # API response types
│   ├── admin.ts
│   ├── user.ts
│   ├── deposit.ts
│   ├── withdrawal.ts
│   ├── pet-type.ts
│   └── task.ts
├── middleware.ts                # Auth middleware
└── package.json
```

---

## Session Notes

### Session 1 (Current)
- Analyzed existing Admin API implementation
- Documented all endpoints with request/response schemas
- Created project structure plan
- Setting up base project...
