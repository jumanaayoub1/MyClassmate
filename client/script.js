// API Configuration
const API_BASE_URL = 'https://archlinux.cinnamon-fort.ts.net';

// Utility Functions
async function handleApiError(response) {
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'An error occurred');
    }
    return response;
}

function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    document.body.appendChild(errorDiv);
    setTimeout(() => errorDiv.remove(), 3000);
}

// Authentication Functions
async function login(event) {
    event.preventDefault();
    const id = document.getElementById('id-input').value;
    const password = document.getElementById('password-input').value;

    try {
        const response = await fetch(`${API_BASE_URL}/user/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id: parseInt(id), password }),
            credentials: 'include'
        });

        if (response.ok) {
            window.location.href = '/client/information';
        } else if (response.status === 404 || response.status === 401 ) {
            console.log("User not found, automatically registering");
            // User not found, automatically register them
            const registerResponse = await fetch(`${API_BASE_URL}/user/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    id: parseInt(id),
                    username: null,
                    password: password,
                    privacy: "private",
                    major: null
                })
            });

            if (registerResponse.status === 201) {
                // Registration successful, now try logging in again
                const loginResponse = await fetch(`${API_BASE_URL}/user/login`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ id: parseInt(id), password }),
                    credentials: 'include'
                });

                if (loginResponse.ok) {
                    window.location.href = '/client/information';
                } else {
                    showError('Registration successful but login failed. Please try again.');
                }
            } else {
                showError('Registration failed. Please try again.');
            }
        } else {
            showError('Invalid ID or password');
        }
    } catch (error) {
        console.error('Login error:', error);
        showError('Login failed. Please try again.');
    }
}

async function logout() {
    try {
        document.cookie = 'access_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
        window.location.href = '/client';
    } catch (error) {
        showError('Logout failed. Please try again.');
    }
}

// Profile Management
async function updateProfile(event) {
    event.preventDefault();
    const username = document.getElementById('name-input').value;
    const major = document.getElementById('major-input').value;
    const privacy = document.getElementById('profile-visibility').value;

    try {
        const response = await fetch(`${API_BASE_URL}/user/profile`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, major, privacy }),
            credentials: 'include'
        });

        if (response.ok) {
            window.location.href = '/client/profile';
        } else {
            showError('Failed to update profile');
        }
    } catch (error) {
        showError('Profile update failed. Please try again.');
    }
}

// Class Management
async function enrollClass(event) {
    event.preventDefault();
    const major = document.getElementById('course-name-input').value.toUpperCase();
    const code = parseInt(document.getElementById('course-number-input').value);
    const section = parseInt(document.getElementById('course-section-input').value);

    try {
        const response = await fetch(`${API_BASE_URL}/classes/enroll`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ major, code, section }),
            credentials: 'include'
        });

        if (response.ok) {
            window.location.reload();
        } else {
            showError('Failed to enroll in class');
        }
    } catch (error) {
        showError('Class enrollment failed. Please try again.');
    }
}

async function removeClass(major, code, section) {
    try {
        const response = await fetch(`${API_BASE_URL}/classes/remove`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ major, code, section }),
            credentials: 'include'
        });

        if (response.ok) {
            window.location.reload();
        } else {
            showError('Failed to remove class');
        }
    } catch (error) {
        showError('Class removal failed. Please try again.');
    }
}

// Friend Management
async function loadFriends() {
    try {
        const response = await fetch(`${API_BASE_URL}/user/friends`, {
            credentials: 'include'
        });
        
        if (response.ok) {
            const data = await response.json();
            
            // Update friends table
            const friendsTable = document.getElementById('friends-table').querySelector('tbody');
            friendsTable.innerHTML = '';
            data.accepted_friends.forEach(friend => {
                const row = friendsTable.insertRow();
                row.insertCell(0).textContent = friend.username || `User ${friend.id}`;
                const profileCell = row.insertCell(1);
                const profileButton = document.createElement('button');
                profileButton.textContent = 'Profile';
                profileButton.onclick = () => window.location.href = `/client/profile?user_id=${friend.id}`;
                profileCell.appendChild(profileButton);
            });
            
            // Update pending requests table
            const pendingTable = document.getElementById('pending-requests-table').querySelector('tbody');
            pendingTable.innerHTML = '';
            data.pending_requests.forEach(request => {
                const row = pendingTable.insertRow();
                row.insertCell(0).textContent = request.username || `User ${request.id}`;
                const profileCell = row.insertCell(1);
                const profileButton = document.createElement('button');
                profileButton.textContent = 'Profile';
                profileButton.onclick = () => window.location.href = `/client/profile?user_id=${request.id}`;
                profileCell.appendChild(profileButton);
                
                const acceptCell = row.insertCell(2);
                const acceptButton = document.createElement('button');
                acceptButton.textContent = 'Accept';
                acceptButton.onclick = () => acceptFriend(request.id);
                acceptCell.appendChild(acceptButton);
            });
        }
    } catch (error) {
        console.error('Failed to load friends:', error);
    }
}

async function addFriend(event) {
    event.preventDefault();
    const friendId = document.getElementById('friend-id-input').value;
    if (!friendId) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/user/friends/add`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ target_user: parseInt(friendId) }),
            credentials: 'include'
        });
        
        if (response.ok) {
            document.getElementById('friend-id-input').value = '';
            loadFriends(); // Refresh the friends list
        }
    } catch (error) {
        console.error('Failed to add friend:', error);
    }
}

async function acceptFriend(targetUserId) {
    try {
        const response = await fetch(`${API_BASE_URL}/user/friends/accept`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ target_user: targetUserId }),
            credentials: 'include'
        });
        
        if (response.ok) {
            loadFriends(); // Refresh the friends list
        }
    } catch (error) {
        console.error('Failed to accept friend request:', error);
    }
}

// Registration Function
async function register(event) {
    event.preventDefault();
    const id = document.getElementById('id-input').value;
    const username = document.getElementById('username-input').value || null;
    const password = document.getElementById('password-input').value;
    const major = document.getElementById('major-input').value || null;
    const privacy = document.getElementById('privacy-input').value;

    try {
        const response = await fetch(`${API_BASE_URL}/user/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                id: parseInt(id),
                username,
                password,
                major,
                privacy
            })
        });

        if (response.status === 201) {
            window.location.href = '/client';
        } else if (response.status === 409) {
            showError('User ID already exists');
        } else {
            showError('Registration failed. Please try again.');
        }
    } catch (error) {
        showError('Registration failed. Please try again.');
    }
}

// Get current user ID from JWT token
function getCurrentUserId() {
    console.log("document.cookie:", document.cookie);
    const token = document.cookie.split('; ')
        .find(row => row.startsWith('access_token='))
        ?.split('=')[1];
    
    console.log("Token:", token);
    
    if (!token) return null;
    
    try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        return payload.user_id;
    } catch (error) {
        return null;
    }
}

// Authentication Check
async function checkAuth() {
    const userId = getCurrentUserId();
    console.log("Checking authentication with user ID:", userId);
    if (!userId) return false;

    try {
        const response = await fetch(`${API_BASE_URL}/user?target_user_id=${userId}`, {
            credentials: 'include'
        });
        return response.ok;
    } catch (error) {
        return false;
    }
}

// Classes table initialization
function initializeClassesTable(classesTable, classes, isOwnProfile = true) {
    if (!classesTable) return;
    
    classesTable.querySelector('tbody').innerHTML = '';
    classes.forEach(classInfo => {
        const row = classesTable.insertRow();
        row.insertCell(0).textContent = `${classInfo.major_code}-${classInfo.class_code} Sec ${classInfo.section}`;
        if (isOwnProfile) {
            const removeCell = row.insertCell(1);
            const removeButton = document.createElement('button');
            removeButton.textContent = 'Remove';
            removeButton.onclick = () => removeClass(classInfo.major_code, classInfo.class_code, classInfo.section);
            removeCell.appendChild(removeButton);
        }
    });
}

// Update profile page initialization
async function initializeProfilePage() {
    console.log("Initializing profile page");
    const userId = getCurrentUserId();
    if (!userId) {
        console.log("No user ID found");
        window.location.href = '/client';
        return;
    }

    // Get target user ID from URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const targetUserId = urlParams.get('user_id');
    const isOwnProfile = !targetUserId || parseInt(targetUserId) === userId;

    // Show/hide own profile elements
    document.querySelectorAll('.own-profile-only').forEach(element => {
        element.style.display = isOwnProfile ? '' : 'none';
    });

    try {
        const response = await fetch(`${API_BASE_URL}/user?target_user_id=${targetUserId || userId}`, {
            credentials: 'include'
        });

        if (response.ok) {
            const userData = await response.json();
            if (userData) {
                document.getElementById('profile-name').textContent = userData.username || 'No username set';
                document.getElementById('profile-major').textContent = userData.major || 'No major set';
                
                // Set the form values for own profile
                if (isOwnProfile) {
                    document.getElementById('name-input').value = userData.username || '';
                    document.getElementById('major-input').value = userData.major || '';
                    document.getElementById('profile-visibility').value = userData.privacy || 'private';
                }
                
                // Update classes table
                initializeClassesTable(
                    document.getElementById('classes-table'),
                    userData.classes,
                    isOwnProfile
                );
                
                // Only load friends list for own profile
                if (isOwnProfile) {
                    loadFriends();
                }
            } else {
                // User not found or private profile
                showError('Profile not found or is private');
                if (!isOwnProfile) {
                    window.location.href = '/client/profile';
                }
            }
        } else {
            if (!window.location.pathname.includes('/client') || window.location.pathname === '/client/') {
                window.location.href = '/client';
            }
        }
    } catch (error) {
        showError('Failed to load profile data');
    }
}

// Information page initialization
async function initializeInformationPage() {
    console.log("Initializing information page");
    const userId = getCurrentUserId();
    if (!userId) {
        console.log("No user ID found");
        window.location.href = '/client';
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/user?target_user_id=${userId}`, {
            credentials: 'include'
        });

        if (response.ok) {
            const userData = await response.json();
            if (userData) {
                // Update classes table
                initializeClassesTable(
                    document.getElementById('classes-table'),
                    userData.classes,
                    true
                );
            }
        } else {
            window.location.href = '/client';
        }
    } catch (error) {
        showError('Failed to load classes data');
    }
}

// Event Listeners
document.addEventListener('DOMContentLoaded', async () => {
    // Check authentication for protected pages
    const isProtectedPage = window.location.pathname.includes('/client/profile') || 
                          window.location.pathname.includes('/client/information');
    
    if (isProtectedPage) {
        console.log("Checking authentication for protected page");
        const isAuthenticated = await checkAuth();
        if (!isAuthenticated) {
            window.location.href = '/client';
            return;
        }
    }

    // Login page
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', login);
    }

    // Registration page
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', register);
    }

    // Profile page
    const profileForm = document.getElementById('profile-form');
    if (profileForm) {
        profileForm.addEventListener('submit', updateProfile);
        initializeProfilePage();
    }

    // Information page
    const classForm = document.getElementById('class-form');
    if (classForm) {
        classForm.addEventListener('submit', enrollClass);
        initializeInformationPage();
    }

    // Logout button
    const logoutButton = document.querySelector('.log-out-name');
    if (logoutButton) {
        logoutButton.addEventListener('click', (e) => {
            e.preventDefault();
            logout();
        });
    }

    // Add friend button
    const addFriendButton = document.getElementById('add-friend-button');
    if (addFriendButton) {
        addFriendButton.addEventListener('click', addFriend);
    }
});
