

---

## 1. Templates Directory Map

താഴെ നൽകിയിരിക്കുന്ന ടേബിളിൽ ഓരോ ആപ്പിലും വരേണ്ട HTML ഫയലുകളും അവയുടെ റൂട്ടും വിശദീകരിച്ചിരിക്കുന്നു.

| Django App | User-facing Templates (`templates/user/...`) | Admin-facing Templates (`templates/admin/...`) |
| :--- | :--- | :--- |
| **accounts** | • `landing_page.html` (Landing/Home)<br>• `signup.html` (Signup form)<br>• `login.html` (User Login)<br>• `userprofile.html` (Dashboard)<br>• `edit_profile.html` (Profile edits)<br>• `change_password.html`<br>• `verify_otp.html` (OTP verify)<br>• `forgot_password.html`<br>• `forgot_password_verify_otp.html`<br>• `reset_password.html`<br>• `verify_email_otp.html` | • `login.html` (Admin login)<br>• `dashboard.html` (Main dashboard panel)<br>• `admin_profile.html` (Admin profile)<br>• `edit_profile.html` (Edit admin profile)<br>• `change_password.html` (Admin password change) |
| **addresses** | • `address_list.html` (Address list)<br>• `add_address.html` (Add new address)<br>• `edit_address.html` (Edit address)<br>• `delete_address.html` (Delete confirmation) | • `customers/customer_list.html` (List of customers)<br>• `customers/customer_details.html` (Customer profile & status) |
| **category** | • *സാധാരണയായി products-ൽ കാണിക്കും, ആവശ്യമെങ്കിൽ:*<br>• `category_grid.html` (Category selection) | • `category/category_list.html` (View all categories)<br>• `category/add_category.html` (Add new category)<br>• `category/edit_category.html` (Edit category) |
| **products** | • `products/prodect_list.html` *(typo: user/products/)* (Product list/grid)<br>• `products/product_detail.html` (Details with size/color selection) | • `products/product_list.html` (Admin product list)<br>• `products/add_product.html` (Add product with variants)<br>• `products/edit_product.html` (Edit details/variants) |
| **cart** | • `cart/cart.html` (Shopping Cart list with quantity updates) | *ആവശ്യമില്ല (Admin views dashboard analytics)* |
| **wishlist** | • `wishlist/wishlist.html` (Items user marked to purchase later) | *ആവശ്യമില്ല* |
| **orders** | • `orders/checkout.html` (Checkout, address & payment select)<br>• `orders/order_success.html` (Success screen)<br>• `orders/order_list.html` (User purchase history)<br>• `orders/order_detail.html` (Details & Cancel/Return option) | • `orders/order_list.html` (Admin list of all orders)<br>• `orders/order_detail.html` (Update order/shipping status) |
| **payments** | • `payments/payment_failed.html` (Transaction failed screen)<br>• `payments/wallet.html` (Optional: Wallet balance & cashback) | *ആവശ്യമില്ല* |
| **offers** | • `offers/offers_list.html` (List of active store coupons/deals) | • `offers/coupon_list.html` (Manage coupons)<br>• `offers/add_coupon.html`<br>• `offers/edit_coupon.html`<br>• `offers/offer_list.html` (Referral & discount offers) |
| **reviews** | • `reviews/add_review.html` (Rating stars & comment form) | • `reviews/review_list.html` (Moderation: approve/delete reviews) |
| **dashboard** | *ആവശ്യമില്ല* | • `dashboard/sales_report.html` (Generate sales PDF/Excel)<br>• `dashboard/statistics.html` (Top-selling products charts) |

---

## 2. Base Templates (Layout Inheritance)

കൂടുതൽ എളുപ്പത്തിൽ ഡിസൈൻ ചെയ്യാനും കോഡ് ആവർത്തിക്കാതിരിക്കാനും (DRY Principle) രണ്ട് പ്രധാന Layout ഫയലുകൾ വേണം. അവ ഇതിനകം `apps/accounts/templates/user/` ഭാഗത്തുണ്ട്.

1. **User Base Layout**: `apps/accounts/templates/user/base.html`
   - Navbar (Home, Products, Categories, Search, Cart, Wishlist, Profile)
   - Message notifications (Toast errors, alerts)
   - Footer (About, Contact, Links)
2. **Admin Base Layout**: `apps/accounts/templates/admin/base.html`
   - Admin Sidebar (Dashboard, Products, Categories, Orders, Customers, Coupons, Reports)
   - Admin Navbar (Profile drop-down, Notifications)

---

## 3. Template Paths (Directory Structure)

നിങ്ങൾ പുതിയ ആപ്പുകളിൽ HTML ഫയലുകൾ നിർമ്മിക്കുമ്പോൾ ഈ താഴെ കൊടുത്തിരിക്കുന്ന ഡയറക്ടറി ഫോർമാറ്റിൽ ചെയ്യുക.

> [!IMPORTANT]
> Django `APP_DIRS: True` ആയതിനാൽ ഓരോ ആപ്പിന്റെ ഉള്ളിലും `templates/` എന്ന ഫോൾഡർ ഉണ്ടാക്കിയാണ് ഇവ വെക്കേണ്ടത്.

### Category App Templates
```text
apps/category/
└── templates/
    └── admin/
        └── category/
            ├── category_list.html
            ├── add_category.html
            └── edit_category.html
```

### Products App Templates
```text
apps/products/
└── templates/
    ├── user/
    │   └── products/
    │       └── product_detail.html     <-- (prodect_list.html നിലവിലുണ്ട്)
    └── admin/
        └── products/
            ├── product_list.html
            ├── add_product.html
            └── edit_product.html
```

### Cart App Templates
```text
apps/cart/
└── templates/
    └── user/
        └── cart/
            └── cart.html
```

### Wishlist App Templates
```text
apps/wishlist/
└── templates/
    └── user/
        └── wishlist/
            └── wishlist.html
```

### Orders App Templates
```text
apps/orders/
└── templates/
    ├── user/
    │   └── orders/
    │       ├── checkout.html
    │       ├── order_success.html
    │       ├── order_list.html
    │       └── order_detail.html
    └── admin/
        └── orders/
            ├── order_list.html
            └── order_detail.html
```

### Offers App Templates
```text
apps/offers/
└── templates/
    ├── user/
    │   └── offers/
    │       └── offers_list.html
    └── admin/
        └── offers/
            ├── coupon_list.html
            ├── add_coupon.html
            ├── edit_coupon.html
            └── offer_list.html
```

### Reviews App Templates
```text
apps/reviews/
└── templates/
    ├── user/
    │   └── reviews/
    │       └── add_review.html
    └── admin/
        └── reviews/
            └── review_list.html
```

### Dashboard App Templates
```text
apps/dashboard/
└── templates/
    └── admin/
        └── dashboard/
            ├── sales_report.html
            └── statistics.html
```
