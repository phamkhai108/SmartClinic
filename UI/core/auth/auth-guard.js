(function () {
    // Configuration for page access control
    const ACCESS_CONFIG = {
        // Pages that only admins can access
        adminOnly: [
            "/core/admin/index.html",
            "/core/admin/files.html",
            "/core/admin/upload.html",
            // // "/core/lung_cancer/lung_cancer_form.html",
            // // "/core/lung_cancer/lung_result.html",
            // "/core/turmor_brain/turmor_brain.html",
            // "/core/turmor_brain/result_predict.html",
        ],

        // Pages that doctors can access
        doctorOnly: [
            // "/core/heart_failure/heart_failure_form.html",
            // "/core/heart_failure/heart_result.html",
            // "/core/chat/chatbot_markdown.html",
            "/core/turmor_brain/turmor_brain.html",
            "/core/turmor_brain/result_predict.html",
        ],

        // Pages that require any authentication (both admin and regular users)
        authRequired: [
            "/core/chat/chatbot_markdown.html",
            "/core/lung_cancer/lung_cancer_form.html",
            "/core/lung_cancer/lung_result.html",
            "/core/heart_failure/heart_failure_form.html",
            "/core/heart_failure/heart_result.html",
        ],

        // Pages that are public (no authentication required)
        public: [
            "/home/main.html",
            "/home/about.html",
            "/core/auth/login.html",
            "/core/auth/register.html",
        ],
    };

    /**
     * Decode JWT token to extract user information
     * @param {string} token - JWT token string
     * @returns {Object} Decoded token payload
     */
    function decodeToken(token) {
        try {
            const base64Url = token.split(".")[1];
            const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
            const jsonPayload = decodeURIComponent(
                atob(base64)
                    .split("")
                    .map(function (c) {
                        return (
                            "%" +
                            ("00" + c.charCodeAt(0).toString(16)).slice(-2)
                        );
                    })
                    .join("")
            );

            return JSON.parse(jsonPayload);
        } catch (error) {
            console.error("Error decoding token:", error);
            return null;
        }
    }

    /**
     * Get user information from localStorage
     * @returns {Object|null} User information or null if not authenticated
     */
    function getUserInfo() {
        const token = localStorage.getItem("accessToken");
        const userInfoStr = localStorage.getItem("userInfo");

        if (!token) return null;

        // Check if token is expired
        try {
            const decodedToken = decodeToken(token);
            if (!decodedToken) return null;

            const currentTime = Math.floor(Date.now() / 1000);
            if (decodedToken.exp && decodedToken.exp < currentTime) {
                // Token expired, clear local storage
                localStorage.removeItem("accessToken");
                localStorage.removeItem("tokenType");
                localStorage.removeItem("userInfo");
                return null;
            }

            // If userInfo is stored, use it; otherwise construct from token
            if (userInfoStr) {
                return JSON.parse(userInfoStr);
            } else {
                return {
                    userId: decodedToken.user_id,
                    userName: decodedToken.user_name,
                    email: decodedToken.email,
                    role: decodedToken.role,
                };
            }
        } catch (error) {
            console.error("Error parsing user info:", error);
            return null;
        }
    }

    /**
     * Check if the user is authenticated
     * @returns {boolean} True if authenticated, false otherwise
     */
    function isAuthenticated() {
        return !!getUserInfo();
    }

    /**
     * Check if the user has admin role
     * @returns {boolean} True if user is admin, false otherwise
     */
    function isAdmin() {
        const userInfo = getUserInfo();
        return userInfo && userInfo.role === "admin";
    }

    /**
     * Check if the user has doctor role
     * @returns {boolean} True if user is doctor, false otherwise
     */
    function isDoctor() {
        const userInfo = getUserInfo();
        return userInfo && userInfo.role === "doctor";
    }

    /**
     * Update UI based on authentication status
     */
    function updateUI() {
        const userInfo = getUserInfo();

        // Update login/register buttons or user profile menu
        const authButtons = document.querySelector(".ms-lg-3.mt-3.mt-lg-0");
        if (authButtons) {
            if (userInfo) {
                // User is logged in - show user profile dropdown
                authButtons.innerHTML = `
                    <div class="dropdown">
                        <button class="btn btn-primary dropdown-toggle rounded-pill px-4 shadow-sm" type="button" id="userDropdown" data-bs-toggle="dropdown" aria-expanded="false">
                            <i class="fas fa-user-circle me-1"></i> ${
                                userInfo.userName
                            }
                        </button>
                        <ul class="dropdown-menu shadow border-0 rounded-3 py-2 dropdown-menu-end" aria-labelledby="userDropdown">
                            ${
                                userInfo.role === "admin"
                                    ? '<li><a class="dropdown-item py-2" href="/core/admin/index.html"><i class="fas fa-tachometer-alt me-1 text-primary"></i> Quản trị hệ thống</a></li>'
                                    : ""
                            }
                            <li><a class="dropdown-item py-2" href="#"><i class="fas fa-user-cog me-1 text-primary"></i> Tài khoản của tôi</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item py-2" href="#" id="logoutBtn"><i class="fas fa-sign-out-alt me-1 text-danger"></i> Đăng xuất</a></li>
                        </ul>
                    </div>
                `;

                // Add logout event listener
                document
                    .getElementById("logoutBtn")
                    .addEventListener("click", function (e) {
                        e.preventDefault();
                        logout();
                    });
            } else {
                // User is not logged in - show login button
                authButtons.innerHTML = `
                    <a href="/core/auth/login.html" class="btn btn-primary rounded-pill px-4 shadow-sm">
                        <i class="fas fa-user me-1"></i> Đăng nhập
                    </a>
                `;
            }
        }
    }

    /**
     * Check if the current page requires specific access permissions
     */
    function checkPageAccess() {
        const currentPath = window.location.pathname;

        // Check if page is admin only
        if (
            ACCESS_CONFIG.adminOnly.some((path) => currentPath.endsWith(path))
        ) {
            if (!isAdmin()) {
                window.location.href =
                    "/core/auth/login.html?redirect=" +
                    encodeURIComponent(currentPath) +
                    "&unauthorized=true";
                return;
            }
        }

        // Check if page is doctor only
        if (
            ACCESS_CONFIG.doctorOnly.some((path) => currentPath.endsWith(path))
        ) {
            if (!isDoctor() && !isAdmin()) {
                window.location.href =
                    "/core/auth/login.html?unauthorized=true";
                return;
            }
        }

        // Check if page requires authentication
        if (
            ACCESS_CONFIG.authRequired.some((path) =>
                currentPath.endsWith(path)
            )
        ) {
            if (!isAuthenticated()) {
                window.location.href =
                    "/core/auth/login.html?redirect=" +
                    encodeURIComponent(currentPath);
                return;
            }
        }

        // For login/register pages, redirect to home if already authenticated
        if (
            (currentPath.endsWith("/core/auth/login.html") ||
                currentPath.endsWith("/core/auth/register.html")) &&
            isAuthenticated()
        ) {
            const userInfo = getUserInfo();
            if (userInfo.role === "admin") {
                window.location.href = "/home/main.html";
            } else if (userInfo.role === "doctor") {
                window.location.href =
                    "/core/heart_failure/heart_failure_form.html";
            } else {
                window.location.href = "/home/main.html";
            }
            return;
        }
    }

    /**
     * Handle user logout
     */
    function logout() {
        localStorage.removeItem("accessToken");
        localStorage.removeItem("tokenType");
        localStorage.removeItem("userInfo");

        // Redirect to homepage after logout
        window.location.href = "/home/main.html";
    }

    /**
     * Initialize authentication functionality
     */
    function init() {
        // Update UI based on authentication status
        updateUI();

        // Check page access permissions
        checkPageAccess();

        // Handle unauthorized messages if redirected from protected page
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.get("unauthorized") === "true") {
            const loginError = document.getElementById("loginError");
            if (loginError) {
                loginError.textContent =
                    "Bạn không có quyền truy cập trang này. Vui lòng đăng nhập với tài khoản có quyền phù hợp.";
                loginError.classList.remove("d-none");
            }
        }
    }

    // Run initialization when DOM is loaded
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }

    // Expose public methods for use in other scripts
    window.AuthGuard = {
        isAuthenticated,
        isAdmin,
        isDoctor,
        getUserInfo,
        logout,
    };
})();
