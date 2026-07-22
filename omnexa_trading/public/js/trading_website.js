/* global frappe */
(function () {
	const STORAGE_LANG = "trading_site_lang";

	const DEFAULT_CATALOG = {
		categories: [
			{ key: "pharma", name_ar: "الأدوية والمستحضرات", name_en: "Pharmaceuticals", icon: "💊", count: 1500 },
			{ key: "medical", name_ar: "المعدات الطبية", name_en: "Medical Equipment", icon: "🏥", count: 800 },
			{ key: "food", name_ar: "الأغذية والمشروبات", name_en: "Food & Beverages", icon: "🍎", count: 2000 },
			{ key: "cosmetics", name_ar: "التجميل والعناية", name_en: "Cosmetics & Care", icon: "✨", count: 500 },
		],
		features: [
			{ icon: "📦", ar: "إدارة المخزون", en: "Inventory Management" },
			{ icon: "🚚", ar: "التوزيع والنقل", en: "Distribution & Logistics" },
			{ icon: "📊", ar: "تحليلات المبيعات", en: "Sales Analytics" },
			{ icon: "🔒", ar: "تتبع المنتجات", en: "Product Tracking" },
			{ icon: "💳", ar: "نقاط البيع", en: "Point of Sale" },
			{ icon: "📱", ar: "تطبيق المبيعات", en: "Mobile Sales" },
		],
	};

	window.TradingSite = {
		config: null,
		lang: localStorage.getItem(STORAGE_LANG) || "ar",
		page: "home",

		init(page) {
			this.page = page || "home";
			this.config = this.defaultConfig();
			this.applyTheme();
			this.renderChrome();
			this.loadConfig()
				.then(() => {
					this.applyTheme();
					this.renderChrome();
					const fn = this[`init_${this.page}`];
					if (typeof fn === "function") fn.call(this);
					this.setupReveal();
				})
				.catch(() => {
					this.config = this.config || this.defaultConfig();
					this.renderChrome();
					const fn = this[`init_${this.page}`];
					if (typeof fn === "function") fn.call(this);
					this.setupReveal();
				});
		},

		defaultConfig() {
			return {
				brand_name_ar: "Omnexa Trading",
				brand_name_en: "Omnexa Trading",
				tagline_ar: "حلول تجارية متكاملة لإدارة سلسلة التوريد",
				tagline_en: "Integrated trading solutions for supply chain management",
				hero_text_ar: "من إدارة المخزون إلى نقاط البيع — منصة واحدة لكل عملياتك التجارية",
				hero_text_en: "From inventory management to point of sale — one platform for all your trading operations",
				hero_image: "https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?auto=format&fit=crop&w=1920&q=85",
				logo: "/assets/omnexa_trading/logo.png",
				primary_color: "#003366",
				secondary_color: "#0A5FA8",
				accent_color: "#00B4D8",
				gold_color: "#D4AF37",
				categories: DEFAULT_CATALOG.categories,
				features: DEFAULT_CATALOG.features,
				stats: { products: 5000, suppliers: 200, customers: 10000, branches: 50 },
			};
		},

		t(key) {
			const map = {
				home: { ar: "الرئيسية", en: "Home" },
				categories: { ar: "التصنيفات", en: "Categories" },
				features: { ar: "المميزات", en: "Features" },
				contact: { ar: "تواصل", en: "Contact" },
				login: { ar: "دخول", en: "Login" },
				get_started: { ar: "ابدأ الآن", en: "Get Started" },
				learn_more: { ar: "اعرف المزيد", en: "Learn More" },
				products: { ar: "منتج", en: "Products" },
				suppliers: { ar: "مورد", en: "Suppliers" },
				customers: { ar: "عميل", en: "Customers" },
				branches: { ar: "فرع", en: "Branches" },
				loading: { ar: "جاري التحميل...", en: "Loading..." },
			};
			return (map[key] && map[key][this.lang]) || key;
		},

		esc(v) {
			if (typeof frappe !== "undefined" && frappe.utils && frappe.utils.escape_html) {
				return frappe.utils.escape_html(v == null ? "" : String(v));
			}
			const d = document.createElement("div");
			d.textContent = v == null ? "" : String(v);
			return d.innerHTML;
		},

		nameField() {
			return this.lang === "ar" ? "brand_name_ar" : "brand_name_en";
		},

		textField(base) {
			return this.lang === "ar" ? `${base}_ar` : `${base}_en`;
		},

		loadConfig() {
			this.config = this.defaultConfig();
			if (this.config.primary_color) {
				document.documentElement.style.setProperty("--trading-primary", this.config.primary_color);
			}
			if (this.config.secondary_color) {
				document.documentElement.style.setProperty("--trading-secondary", this.config.secondary_color);
			}
			if (this.config.accent_color) {
				document.documentElement.style.setProperty("--trading-teal", this.config.accent_color);
			}
			if (this.config.gold_color) {
				document.documentElement.style.setProperty("--trading-gold", this.config.gold_color);
			}
			return Promise.resolve();
		},

		applyTheme() {
			const root = document.querySelector(".trading-site");
			if (!root) return;
			root.dir = this.lang === "ar" ? "rtl" : "ltr";
			root.lang = this.lang;
		},

		toggleLang() {
			this.lang = this.lang === "ar" ? "en" : "ar";
			localStorage.setItem(STORAGE_LANG, this.lang);
			this.applyTheme();
			this.renderChrome();
			const fn = this[`init_${this.page}`];
			if (typeof fn === "function") fn.call(this);
		},

		setupReveal() {
			const els = document.querySelectorAll(".trading-reveal");
			if (!els.length || !("IntersectionObserver" in window)) {
				els.forEach((el) => el.classList.add("trading-visible"));
				return;
			}
			const obs = new IntersectionObserver(
				(entries) => {
					entries.forEach((e) => {
						if (e.isIntersecting) {
							e.target.classList.add("trading-visible");
							obs.unobserve(e.target);
						}
					});
				},
				{ threshold: 0.12 }
			);
			els.forEach((el) => obs.observe(el));
		},

		renderChrome() {
			const cfg = this.config || this.defaultConfig();
			const name = cfg[this.nameField()] || "Trading";
			const logo = cfg.logo
				? `<img src="${this.esc(cfg.logo)}" alt="" onerror="this.style.display='none'">`
				: "📦";
			const nav = [
				{ href: "/trading", key: "home", page: "home" },
				{ href: "/trading#trading-categories-section", key: "categories", page: "home" },
				{ href: "/trading#trading-features-section", key: "features", page: "home" },
				{ href: "/trading#trading-stats", key: "stats", page: "home" },
			];

			const header = document.getElementById("trading-header");
			if (header) {
				header.innerHTML = `
					<div class="trading-topbar"><div class="trading-wrap trading-topbar-inner">
						<span>📞 +966 11 000 0000</span>
						<span>✉ sales@omnexa.trading</span>
						<span class="trading-topbar-links">
							<a href="/app/trading-workcenter">${this.lang === "ar" ? "مركز العمل" : "Workcenter"}</a>
							<a href="/app/trading-customer-portal">${this.lang === "ar" ? "بوابة العملاء" : "Customer Portal"}</a>
						</span>
					</div></div>
					<div class="trading-wrap trading-header-inner">
						<a class="trading-brand trading-brand-stack" href="/trading">
							<span class="trading-brand-logo">${logo}</span>
							<span class="trading-brand-name">${this.esc(name)}</span>
						</a>
						<button type="button" class="trading-mobile-toggle" id="trading-menu-toggle" aria-label="Menu">☰</button>
						<nav class="trading-nav trading-nav-single" id="trading-nav">
							<div class="trading-nav-links">
							${nav
								.map((n) => {
									const label = this.t(n.key);
									const active = n.page && this.page === n.page ? "active" : "";
									return `<a href="${n.href}" class="${active}">${label}</a>`;
								})
								.join("")}
							</div>
						</nav>
						<div class="trading-actions">
							<button type="button" class="trading-lang" id="trading-lang-toggle">${this.lang === "ar" ? "EN" : "AR"}</button>
							<a class="trading-btn trading-btn-outline" href="/login">${this.t("login")}</a>
							<a class="trading-btn trading-btn-primary" href="/app/trading-workcenter">${this.t("get_started")}</a>
						</div>
					</div>`;
				document.getElementById("trading-lang-toggle")?.addEventListener("click", () => this.toggleLang());
				document.getElementById("trading-menu-toggle")?.addEventListener("click", () => {
					document.getElementById("trading-nav")?.classList.toggle("open");
				});
			}

			const footer = document.getElementById("trading-footer");
			if (footer) {
				footer.innerHTML = `
					<div class="trading-wrap trading-footer-grid">
						<div>
							<h3>${this.esc(name)}</h3>
							<p>${this.esc(cfg[this.textField("hero_text")] || "")}</p>
							<p class="trading-footer-contact">📞 +966 11 000 0000 · ✉ sales@omnexa.trading</p>
						</div>
						<div>
							<h4>${this.lang === "ar" ? "التصنيفات" : "Categories"}</h4>
							<p><a href="/trading#trading-categories-section">${this.lang === "ar" ? "الأدوية" : "Pharmaceuticals"}</a></p>
							<p><a href="/trading#trading-categories-section">${this.lang === "ar" ? "المعدات الطبية" : "Medical Equipment"}</a></p>
							<p><a href="/trading#trading-categories-section">${this.lang === "ar" ? "الأغذية" : "Food & Beverages"}</a></p>
						</div>
						<div>
							<h4>${this.lang === "ar" ? "المميزات" : "Features"}</h4>
							<p><a href="/trading#trading-features-section">${this.lang === "ar" ? "إدارة المخزون" : "Inventory"}</a></p>
							<p><a href="/trading#trading-features-section">${this.lang === "ar" ? "نقاط البيع" : "Point of Sale"}</a></p>
							<p><a href="/trading#trading-features-section">${this.lang === "ar" ? "تطبيق المبيعات" : "Mobile Sales"}</a></p>
						</div>
						<div>
							<h4>${this.lang === "ar" ? "البوابات" : "Portals"}</h4>
							<p><a href="/app/trading-workcenter">${this.lang === "ar" ? "مركز العمل" : "Workcenter"}</a></p>
							<p><a href="/app/trading-customer-portal">${this.lang === "ar" ? "بوابة العملاء" : "Customer Portal"}</a></p>
						</div>
					</div>
					<div class="trading-wrap trading-footer-bottom">© ${new Date().getFullYear()} ${this.esc(name)} · Omnexa · ErpGenEx</div>`;
			}
		},

		init_home() {
			const cfg = this.config || {};
			const heroImg = cfg.hero_image || "";
			const hero = document.getElementById("trading-hero");
			if (hero) {
				hero.innerHTML = `
					<div class="trading-hero-bg" style="background-image:url('${this.esc(heroImg)}')"></div>
					<div class="trading-hero-overlay"></div>
					<div class="trading-wrap trading-hero-premium-inner">
						<span class="trading-eyebrow trading-eyebrow-light">Omnexa Trading · Global Supply Chain</span>
						<h1>${this.esc(cfg[this.textField("tagline")] || "")}</h1>
						<p class="trading-hero-lead">${this.esc(cfg[this.textField("hero_text")] || "")}</p>
						<div class="trading-hero-cta">
							<a class="trading-btn trading-btn-accent" href="/app/trading-workcenter">${this.lang === "ar" ? "ابدأ الآن" : "Get Started"}</a>
							<a class="trading-btn trading-btn-ghost-light" href="/trading#trading-categories-section">${this.lang === "ar" ? "استكشف التصنيفات" : "Explore Categories"}</a>
						</div>
					</div>`;
			}

			const trust = document.getElementById("trading-trust-strip");
			if (trust) {
				const values = (cfg.features || DEFAULT_CATALOG.features).slice(0, 5);
				trust.innerHTML = `<div class="trading-wrap trading-value-inner">${values
					.map((v) => `<div class="trading-value-item"><span>${v.icon}</span><strong>${this.lang === "ar" ? v.ar : v.en}</strong></div>`)
					.join("")}</div>`;
			}

			const categories = document.getElementById("trading-categories-section");
			if (categories) {
				const cats = cfg.categories || DEFAULT_CATALOG.categories;
				categories.innerHTML = `
					<div class="trading-wrap">
						<div class="trading-section-title">
							<span class="trading-eyebrow">Product Categories</span>
							<h2>${this.lang === "ar" ? "تصنيفات المنتجات" : "Product Categories"}</h2>
							<p>${this.lang === "ar" ? "مجموعة واسعة من المنتجات لجميع احتياجاتك التجارية" : "Wide range of products for all your trading needs"}</p>
						</div>
						<div class="trading-grid-4">${cats
							.map((c) => `<div class="trading-card">
								<div style="font-size:48px;margin-bottom:16px;">${c.icon}</div>
								<h3>${this.esc(this.lang === "ar" ? c.name_ar : c.name_en)}</h3>
								<p>${this.esc(String(c.count || 0))}+ ${this.lang === "ar" ? "منتج" : "products"}</p>
							</div>`
							)
							.join("")}</div>
					</div>`;
			}

			const features = document.getElementById("trading-features-section");
			if (features) {
				const feats = cfg.features || DEFAULT_CATALOG.features;
				features.innerHTML = `
					<div class="trading-wrap">
						<div class="trading-section-title">
							<span class="trading-eyebrow">Key Features</span>
							<h2>${this.lang === "ar" ? "المميزات الرئيسية" : "Key Features"}</h2>
							<p>${this.lang === "ar" ? "حلول متكاملة لإدارة جميع عملياتك التجارية" : "Integrated solutions for all your trading operations"}</p>
						</div>
						<div class="trading-grid-4">${feats
							.map((f) => `<div class="trading-card">
								<div style="font-size:32px;margin-bottom:12px;">${f.icon}</div>
								<h3>${this.esc(this.lang === "ar" ? f.ar : f.en)}</h3>
							</div>`
							)
							.join("")}</div>
					</div>`;
			}

			const stats = document.getElementById("trading-stats");
			if (stats && cfg.stats) {
				const s = cfg.stats;
				stats.innerHTML = `
					<div class="trading-wrap trading-stats-grid">
						<div><div class="trading-stat-num">${s.products || 0}</div><div class="trading-stat-label">${this.t("products")}</div></div>
						<div><div class="trading-stat-num">${s.suppliers || 0}</div><div class="trading-stat-label">${this.t("suppliers")}</div></div>
						<div><div class="trading-stat-num">${s.customers || 0}</div><div class="trading-stat-label">${this.t("customers")}</div></div>
						<div><div class="trading-stat-num">${s.branches || 0}</div><div class="trading-stat-label">${this.t("branches")}</div></div>
					</div>`;
			}

			const cta = document.getElementById("trading-cta-band");
			if (cta) {
				cta.innerHTML = `
					<div class="trading-wrap">
						<h2>${this.lang === "ar" ? "جاهز لتحويل عملياتك التجارية؟" : "Ready to transform your trading operations?"}</h2>
						<p>${this.lang === "ar" ? "انضم إلى آلاف التجار الذين يستخدمون Omnexa Trading" : "Join thousands of traders using Omnexa Trading"}</p>
						<div class="trading-hero-cta">
							<a class="trading-btn trading-btn-accent" href="/app/trading-workcenter">${this.lang === "ar" ? "ابدأ الآن" : "Get Started"}</a>
							<a class="trading-btn trading-btn-ghost-light" href="/trading#trading-features-section">${this.t("learn_more")}</a>
						</div>
					</div>`;
			}
		},
	};
})();
