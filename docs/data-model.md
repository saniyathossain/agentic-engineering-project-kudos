# Data model

```mermaid
erDiagram
    USERS ||--o{ SPACES : owns
    SPACES ||--o{ TESTIMONIALS : receives
    USERS ||--o{ SUBSCRIPTIONS : has
    SUBSCRIPTIONS ||--o{ SUBSCRIPTION_ITEMS : contains

    USERS {
        bigint id PK
        string name
        string email UK
        string password
        timestamp email_verified_at
        timestamp banner_dismissed_at
        string stripe_id "Cashier"
        string pm_type "Cashier"
        string pm_last_four "Cashier"
    }
    SPACES {
        bigint id PK
        ulid public_id UK
        bigint user_id FK
        string name
        string slug UK
        string logo_path
        string header_title
        text message "markdown"
        bool collect_rating
        string theme "light|dark|brand"
        jsonb fields "company,title,social_link,photo: enabled+required"
        bool is_accepting
    }
    TESTIMONIALS {
        bigint id PK
        ulid public_id UK
        bigint space_id FK
        smallint rating "1-5 nullable"
        text body
        string respondent_name
        string respondent_email "never public"
        string company
        string title
        string social_link
        string photo_path
        bool consent
        string status "pending|published|hidden"
        bool is_favorite
        timestamp submitted_at
    }
    SUBSCRIPTIONS {
        bigint id PK
        bigint user_id FK
        string type
        string stripe_id UK
        string stripe_status
    }
    SUBSCRIPTION_ITEMS {
        bigint id PK
        bigint subscription_id FK
        string stripe_price
    }
```

Indexes: `spaces(slug)`, `spaces(user_id)`, `testimonials(space_id, submitted_at)`, `testimonials(space_id, status)`.
Rules: name + email are always collected; `fields` only configures optional ones. Deleting a space cascades to its testimonials. Subscription tables are Cashier's standard schema (added in the billing unit).
