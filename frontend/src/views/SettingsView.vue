<template>
    <div class="settings-container">
        <!-- Navbar -->
        <!-- <nav class="navbar">
      <span class="brand">⚙ Settings</span>
      <div class="nav-links">
        <router-link to="/cloud" class="nav-link">PocketShelf</router-link>
        <button v-if="auth.user" class="btn-logout" @click="handleLogout">Logout</button>
        <router-link v-else to="/login" class="nav-link">Login</router-link>
      </div>
    </nav> -->

        <!-- Settings Content -->
        <div class="settings-content">
            <h1>Account Settings</h1>
            <p class="subtitle">Manage your account information</p>

            <div class="settings-form">
                <!-- Hostname Field -->
                <div class="form-group">
                    <label for="hostname">Hostname</label>
                    <input
                        id="hostname"
                        v-model="formData.hostname"
                        type="text"
                        class="form-input"
                        :disabled="disabledFields.hostname"
                    />
                </div>

                <!-- Email Field -->
                <div class="form-group">
                    <label for="email">Email</label>
                    <input
                        id="email"
                        v-model="formData.email"
                        type="email"
                        class="form-input"
                        :disabled="disabledFields.email"
                    />
                </div>

                <!-- Password Field -->
                <div class="form-group">
                    <label for="password">Password</label>
                    <div class="password-wrapper">
                        <input
                            id="password"
                            v-model="formData.password"
                            :type="showPassword ? 'text' : 'password'"
                            class="form-input"
                            :disabled="disabledFields.password"
                            placeholder="••••••••"
                        />
                        <button
                            v-if="!disabledFields.password"
                            @click="togglePasswordVisibility"
                            class="toggle-password-btn"
                            type="button"
                        >
                            {{ showPassword ? "👁 Hide" : "👁 Show" }}
                        </button>
                    </div>
                </div>

                <!-- Submit Button -->
                <button
                    @click="handleSubmit"
                    class="btn-submit"
                    :disabled="!hasChanges"
                >
                    Save Changes
                </button>

                <!-- Confirmation Modal -->
                <div v-if="showConfirmation" class="confirmation-modal">
                    <div class="modal-content">
                        <h2>Are you sure?</h2>
                        <p>
                            Do you want to save these changes to your account?
                        </p>
                        <div class="modal-buttons">
                            <button @click="confirmChanges" class="btn-yes">
                                Yes
                            </button>
                            <button @click="cancelChanges" class="btn-no">
                                No
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Success/Error Messages -->
                <div v-if="message" :class="['message', message.type]">
                    {{ message.text }}
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useAuthStore } from "../stores/auth.js";
import { useRouter } from "vue-router";

const auth = useAuthStore();
const router = useRouter();

const formData = ref({
    hostname: "",
    email: "",
    password: "",
});

const originalData = ref({
    hostname: "",
    email: "",
    password: "",
});

const showPassword = ref(false);
const showConfirmation = ref(false);
const message = ref(null);

const disabledFields = ref({
    hostname: true,
    email: true,
    password: true,
});

const hasChanges = computed(() => {
    return (
        formData.value.hostname !== originalData.value.hostname ||
        formData.value.email !== originalData.value.email ||
        formData.value.password !== originalData.value.password
    );
});

onMounted(() => {
    if (auth.user) {
        // Populate form with user data
        formData.value.hostname = auth.user.username || "";
        formData.value.email = auth.user.email || "";
        formData.value.password = "••••••••"; // Masked password

        // Store original values
        originalData.value = { ...formData.value };

        // Enable editing
        disabledFields.value.hostname = false;
        disabledFields.value.email = false;
        disabledFields.value.password = false;
    }
});

function togglePasswordVisibility() {
    showPassword.value = !showPassword.value;
}

function handleSubmit() {
    // Validate that at least one field has changed
    if (!hasChanges.value) {
        message.value = {
            type: "info",
            text: "No changes detected.",
        };
        setTimeout(() => {
            message.value = null;
        }, 3000);
        return;
    }

    // Show confirmation modal
    showConfirmation.value = true;
}

function confirmChanges() {
    showConfirmation.value = false;

    // Simulate API call delay
    setTimeout(() => {
        // Update the auth store with new data
        if (auth.user) {
            auth.user.username = formData.value.hostname;
            auth.user.email = formData.value.email;
            // Note: Password update would be handled by API in production
        }

        // Update original data to reflect saved changes
        originalData.value = { ...formData.value };

        // Show success message
        message.value = {
            type: "success",
            text: "Account settings updated successfully!",
        };

        // Clear message after 3 seconds
        setTimeout(() => {
            message.value = null;
        }, 3000);
    }, 500);
}

function cancelChanges() {
    showConfirmation.value = false;
    // Revert to original values
    formData.value = { ...originalData.value };
    showPassword.value = false;
    message.value = {
        type: "info",
        text: "Changes cancelled.",
    };
    setTimeout(() => {
        message.value = null;
    }, 2000);
}

function handleLogout() {
    auth.logout();
    router.push("/login");
}
</script>

<style scoped>
.settings-container {
    min-height: 100vh;
    background: #f0f2f5;
}

.navbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.75rem 2rem;
    background: #1a73e8;
    color: #fff;
}

.brand {
    font-size: 1.2rem;
    font-weight: 700;
}

.nav-links {
    display: flex;
    align-items: center;
    gap: 1.5rem;
}

.nav-link {
    color: #fff;
    text-decoration: none;
    font-weight: 500;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    transition: background 0.3s ease;
}

.nav-link:hover {
    background: rgba(255, 255, 255, 0.2);
}

.btn-logout {
    background: transparent;
    border: 1px solid #fff;
    color: #fff;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    cursor: pointer;
    font-weight: 500;
    transition: all 0.3s ease;
}

.btn-logout:hover {
    background: #fff;
    color: #1a73e8;
}

.settings-content {
    max-width: 600px;
    margin: 2rem auto;
    padding: 2rem;
}

.settings-content h1 {
    color: #333;
    margin-bottom: 0.5rem;
    font-size: 2rem;
}

.subtitle {
    color: #666;
    margin-bottom: 2rem;
    font-size: 1rem;
}

.settings-form {
    background: #fff;
    padding: 2rem;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.form-group {
    margin-bottom: 1.5rem;
}

.form-group label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 600;
    color: #333;
}

.form-input {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 1rem;
    transition: border-color 0.3s ease;
}

.form-input:focus {
    outline: none;
    border-color: #1a73e8;
    box-shadow: 0 0 0 3px rgba(26, 115, 232, 0.1);
}

.form-input:disabled {
    background: #f5f5f5;
    color: #999;
    cursor: not-allowed;
}

.password-wrapper {
    position: relative;
}

.password-wrapper .form-input {
    padding-right: 5rem;
}

.toggle-password-btn {
    position: absolute;
    right: 0.5rem;
    top: 50%;
    transform: translateY(-50%);
    background: none;
    border: none;
    color: #1a73e8;
    cursor: pointer;
    font-size: 0.85rem;
    padding: 0.5rem;
    transition: color 0.3s ease;
}

.toggle-password-btn:hover {
    color: #1557b0;
}

.btn-submit {
    width: 100%;
    padding: 0.75rem;
    background: #1a73e8;
    color: #fff;
    border: none;
    border-radius: 4px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    margin-top: 1rem;
}

.btn-submit:hover:not(:disabled) {
    background: #1557b0;
    box-shadow: 0 4px 12px rgba(26, 115, 232, 0.3);
}

.btn-submit:disabled {
    background: #ccc;
    cursor: not-allowed;
}

.confirmation-modal {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
}

.modal-content {
    background: #fff;
    padding: 2rem;
    border-radius: 8px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    text-align: center;
    max-width: 400px;
}

.modal-content h2 {
    color: #333;
    margin-bottom: 1rem;
}

.modal-content p {
    color: #666;
    margin-bottom: 2rem;
}

.modal-buttons {
    display: flex;
    gap: 1rem;
    justify-content: center;
}

.btn-yes,
.btn-no {
    padding: 0.75rem 2rem;
    border: none;
    border-radius: 4px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    flex: 1;
}

.btn-yes {
    background: #34a853;
    color: #fff;
}

.btn-yes:hover {
    background: #2d8e47;
    box-shadow: 0 4px 12px rgba(52, 168, 83, 0.3);
}

.btn-no {
    background: #ea4335;
    color: #fff;
}

.btn-no:hover {
    background: #d33425;
    box-shadow: 0 4px 12px rgba(234, 67, 53, 0.3);
}

.message {
    margin-top: 1.5rem;
    padding: 1rem;
    border-radius: 4px;
    font-weight: 500;
    text-align: center;
}

.message.success {
    background: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
}

.message.error {
    background: #f8d7da;
    color: #721c24;
    border: 1px solid #f5c6cb;
}

.message.info {
    background: #d1ecf1;
    color: #0c5460;
    border: 1px solid #bee5eb;
}

@media (max-width: 600px) {
    .settings-content {
        margin: 1rem;
        padding: 1rem;
    }

    .navbar {
        flex-direction: column;
        gap: 1rem;
    }

    .nav-links {
        width: 100%;
        justify-content: space-between;
    }

    .settings-form {
        padding: 1.5rem;
    }
}
</style>
