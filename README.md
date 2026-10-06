# BAM Wallet & Transfers
## Documentation

### Run Project
```bash
# Install dependencies
flutter pub get

# Generate Freezed/JSON code
dart run build_runner build --delete-conflicting-outputs

# Generate l10n files
flutter gen-l10n

# Run the app
flutter run

# Clean build
flutter clean
```

### Login Authentication

**Firebase Auth:** [Firebase](https://firebase.google.com/?hl=es-419)
| Email | Password | Role |
|-------|----------|------|
| `juan.balan@bam.com.gt` | `prueba123` | admin |
| `juanpablobc7@gmail.com` | `prueba123` | user |

**DummyJSON:** [DummyJSON - Auth](https://dummyjson.com/docs/auth)
| Username | Password |
|----------|----------|
| `emilys` | `emilyspass` |

### Feature Flags
This project uses feature flags to control environment-specific behavior. All flags are centralized in:
`lib/core/config/feature_flags.dart`

| Flag | Description |
|------|-------------|
| `useFirebaseAuth` | Use Firebase Auth (true) or DummyJSON/mock (false) |
| `useDummyJsonApi` | Use real DummyJSON API when Firebase is disabled |
| `useOnboardingLogic` | Control onboarding flow behavior |

### Roles
| Role | Permissions |
|------|-------------|
| `admin` | Full access: edit products, view all orders, receive all notifications |
| `user` | Own data only: transactions, orders, cart, favorites |

### Firestore Collections
| Collection | Purpose |
|------------|---------|
| `users` | User roles and display names |
| `accounts` | Financial accounts (balance, currency) |
| `transactions` | Transaction history (paginated queries) |
| `products` | E-commerce products |
| `orders` | Cart purchase orders |

### Notifications
| Type | Trigger |
|------|---------|
| In-app (TopNotification) | UI actions (add to cart, transfer, errors) |
| Firestore Streams | New order detected in real-time |
| Local notification | Checkout completed |
| Push (FCM) | Sent manually from Firebase Console → Messaging |

### Push Notifications Setup
1. Run the app → copy the FCM token from debug console
2. Firebase Console → Messaging → Create campaign → Send test message
3. Paste the FCM token → Send

**Note:** iOS push requires Apple Developer Program ($99/year) + APNs key configuration. Android works immediately.

## Project Structure
```
lib/
├── core/
│   ├── assets/              # Fonts, images
│   ├── config/              # Feature flags
│   ├── constants/           # Theme colors
│   ├── network/             # API client, exceptions, services
│   ├── providers/           # Shared providers (locale, role, user, services)
│   ├── routing/             # GoRouter with auth guards
│   ├── services/            # Notification services (local, push, order stream)
│   ├── utils/               # Validators, category icons
│   └── widgets/             # Reusable widgets (TopNotification, ProductCard, etc.)
├── features/
│   ├── auth/                # Authentication (Clean Architecture)
│   │   ├── data/            # Datasources (remote, local, firebase) + repository
│   │   ├── domain/          # Entities, use cases, repository contract
│   │   └── presentation/    # Riverpod providers + Freezed state
│   ├── layouts/             # Admin layout with bottom navigation
│   └── pages/
│       ├── admin/
│       │   ├── configuration/
│       │   ├── dashboard/       # With local cache (SharedPreferences)
│       │   ├── ecommerce/       # Products, cart, favorites, edit (admin), checkout
│       │   ├── history/         # Paginated transactions from Firestore
│       │   ├── product_detail/  # Product detail with add-to-cart
│       │   ├── profile/
│       │   └── trasnfers/       # Transfer form → saves to Firestore
│       ├── auth/                # Login, forgot password
│       └── core/                # Splash, onboarding
└── l10n/                    # Localization files (EN/ES)
```

## Tech Stack
| Category | Technology |
|----------|-----------|
| Framework | Flutter 3.38+ |
| State Management | Riverpod |
| Navigation | GoRouter |
| HTTP Client | Dio |
| Auth | Firebase Auth + DummyJSON |
| Database | Cloud Firestore |
| Push Notifications | Firebase Cloud Messaging |
| Local Notifications | flutter_local_notifications |
| Secure Storage | flutter_secure_storage |
| Code Generation | Freezed + json_serializable |
| Linting | flutter_lints |
| i18n | Flutter Localizations (ARB) |

## Detailed Documentation
See [R-PROJECT-SUMMARY.md](R-PROJECT-SUMMARY.md) for full technical documentation.

## Deliveries
See [R-DELIVERIES.md](R-DELIVERIES.md) for sprint deliveries.

this is a test