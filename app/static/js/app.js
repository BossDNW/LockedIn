// ========== EXISTING CODE - DO NOT REMOVE ==========
async function getUserData(){
    const response = await fetch('/api/users');
    return response.json();
}

function loadTable(users){
    const table = document.querySelector('#result');
    if (!table) return; // Only run if #result element exists
    for(let user of users){
        table.innerHTML += `<tr>
            <td>${user.id}</td>
            <td>${user.username}</td>
        </tr>`;
    }
}

async function main(){
    const users = await getUserData();
    loadTable(users);
}

// Only run the existing main() if we're on a page that has #result element
if (document.querySelector('#result')) {
    main();
}
// ========== END EXISTING CODE ==========

// ========== NEW CODE FOR PROGRAMMES SEARCH AND FILTER ==========
// Global variables for programmes functionality
let currentPage = 1;
let currentQuery = "";
let currentAcademicYear = null;
let currentCredits = null;
let totalPages = 1;

// Function to search programmes
async function searchProgrammes(page = 1) {
    const searchInput = document.querySelector('.search-bar');
    const academicYearFilter = document.querySelector('#academic-year-filter');
    const creditsFilter = document.querySelector('#credits-filter');
    
    // Only run if we're on the programmes page
    if (!searchInput) return;
    
    const query = searchInput ? searchInput.value : '';
    const academicYear = academicYearFilter ? academicYearFilter.value : '';
    const credits = creditsFilter ? creditsFilter.value : '';
    
    // Build URL with query parameters
    let url = `/api/programmes/search?page=${page}&limit=10`;
    if (query) url += `&q=${encodeURIComponent(query)}`;
    if (academicYear && academicYear !== 'all') url += `&academic_year=${academicYear}`;
    if (credits && credits !== 'all') url += `&credits=${credits}`;
    
    try {
        const response = await fetch(url);
        const result = await response.json();
        
        currentPage = result.pagination.current_page;
        totalPages = result.pagination.total_pages;
        currentQuery = query;
        currentAcademicYear = academicYear;
        currentCredits = credits;
        
        loadProgrammesTable(result.data);
        updatePagination(result.pagination);
        
        // Select first item by default
        if (result.data.length > 0) {
            renderDetail(result.data[0]);
        } else {
            const detailView = document.getElementById("detail");
            if (detailView) {
                detailView.innerHTML = `
                    <div class="detail-view">
                        <p>No programmes found. Try adjusting your search criteria.</p>
                    </div>
                `;
            }
        }
        
    } catch (error) {
        console.error('Error searching programmes:', error);
    }
}

// Function to load programmes into the master list
function loadProgrammesTable(programmes) {
    const masterList = document.getElementById("master");
    if (!masterList) return;
    
    masterList.innerHTML = "";
    
    for (let programme of programmes) {
        let div = document.createElement("div");
        div.className = "master-item";
        div.setAttribute("data-id", programme.id);
        div.innerHTML = `
            <div class="item-content">
                <h2>${escapeHtml(programme.title)}</h2>
                <p>${escapeHtml(programme.company_name)}, ${escapeHtml(programme.company_location || 'Location not specified')}</p>
                <div class="item-tags">
                    <span>Year: ${programme.academic_year}</span>
                    <span>Credits: ${programme.credits}</span>
                    <span>${escapeHtml(programme.compensation || 'Not specified')}</span>
                </div>
            </div>
        `;
        div.onclick = function () {
            let allItems = document.querySelectorAll(".master-item");
            for (let j = 0; j < allItems.length; j++) {
                allItems[j].classList.remove("active");
            }
            this.classList.add("active");
            renderDetail(programme);
        };
        masterList.appendChild(div);
    }
}

// Function to render detail view
function renderDetail(programme) {
    const detailView = document.getElementById("detail");
    if (!detailView) return;
    
    detailView.innerHTML = `
        <div class="detail-view">
            <h2>${escapeHtml(programme.title)}</h2>
            <div class="company-info">
                <p><strong>Company:</strong> ${escapeHtml(programme.company_name)}</p>
                <p><strong>Location:</strong> ${escapeHtml(programme.company_location || 'Not specified')}</p>
            </div>
            
            <div class="programme-details">
                <h3>Programme Details</h3>
                <p><strong>Academic Year:</strong> ${programme.academic_year}</p>
                <p><strong>Credits:</strong> ${programme.credits}</p>
                <p><strong>Compensation:</strong> ${escapeHtml(programme.compensation || 'Not specified')}</p>
                <p><strong>Schedule:</strong> ${escapeHtml(programme.schedule || 'Not specified')}</p>
                <p><strong>Work Site:</strong> ${escapeHtml(programme.work_site || 'Not specified')}</p>
                ${programme.keywords ? `<p><strong>Keywords:</strong> ${escapeHtml(programme.keywords)}</p>` : ''}
            </div>
            
            <div class="programme-description">
                <h3>Description</h3>
                <p>${escapeHtml(programme.description || 'No description available.')}</p>
            </div>
            
            <button class="apply-btn" onclick="applyToProgramme(${programme.id})">Apply Now</button>
        </div>
    `;
}

// Function to update pagination controls
function updatePagination(pagination) {
    const paginationContainer = document.querySelector('.pagination');
    if (!paginationContainer) return;
    
    let html = '';
    
    // Previous button
    if (pagination.has_prev) {
        html += `<button onclick="changePage(${pagination.prev_page})">Previous</button>`;
    } else {
        html += `<button disabled>Previous</button>`;
    }
    
    // Page numbers
    for (let i = 1; i <= pagination.total_pages; i++) {
        if (i === pagination.current_page) {
            html += `<button class="active-page" disabled>${i}</button>`;
        } else if (Math.abs(i - pagination.current_page) <= 2 || i === 1 || i === pagination.total_pages) {
            html += `<button onclick="changePage(${i})">${i}</button>`;
        } else if (Math.abs(i - pagination.current_page) === 3) {
            html += `<button disabled>...</button>`;
        }
    }
    
    // Next button
    if (pagination.has_next) {
        html += `<button onclick="changePage(${pagination.next_page})">Next</button>`;
    } else {
        html += `<button disabled>Next</button>`;
    }
    
    paginationContainer.innerHTML = html;
}

// Function to change page
function changePage(page) {
    if (page >= 1 && page <= totalPages) {
        searchProgrammes(page);
    }
}

// Function to load filter options
async function loadFilterOptions() {
    try {
        const response = await fetch('/api/programmes/filters/options');
        const options = await response.json();
        
        // Populate academic year filter
        const academicFilter = document.querySelector('#academic-year-filter');
        if (academicFilter && options.academic_years) {
            academicFilter.innerHTML = '<option value="all">All Years</option>';
            options.academic_years.forEach(year => {
                academicFilter.innerHTML += `<option value="${year}">${year}</option>`;
            });
        }
        
        // Populate credits filter
        const creditsFilter = document.querySelector('#credits-filter');
        if (creditsFilter && options.credits) {
            creditsFilter.innerHTML = '<option value="all">All Credits</option>';
            options.credits.forEach(credit => {
                creditsFilter.innerHTML += `<option value="${credit}">${credit} credits</option>`;
            });
        }
    } catch (error) {
        console.error('Error loading filter options:', error);
    }
}

// Function to apply to a programme
async function applyToProgramme(programmeId) {
    try {
        const response = await fetch('/api/applications', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ programmeId: programmeId })
        });
        
        if (response.ok) {
            alert('Successfully applied to the programme!');
            // Optionally refresh the page or update UI
        } else {
            const error = await response.json();
            alert(error.detail || 'Failed to apply. Please try again.');
        }
    } catch (error) {
        console.error('Error applying to programme:', error);
        alert('An error occurred. Please try again.');
    }
}

// Helper function to escape HTML
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Debounce function for search input
function debounce(func, delay) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, delay);
    };
}

// Initialize programmes functionality only on programmes page
async function initProgrammesPage() {
    // Check if we're on the programmes page
    const masterList = document.getElementById("master");
    if (!masterList) return;
    
    // Load filter options
    await loadFilterOptions();
    
    // Load initial programmes
    await searchProgrammes(1);
    
    // Setup event listeners
    const searchBar = document.querySelector('.search-bar');
    if (searchBar) {
        searchBar.addEventListener('input', debounce(() => searchProgrammes(1), 500));
    }
    
    const academicFilter = document.querySelector('#academic-year-filter');
    if (academicFilter) {
        academicFilter.addEventListener('change', () => searchProgrammes(1));
    }
    
    const creditsFilter = document.querySelector('#credits-filter');
    if (creditsFilter) {
        creditsFilter.addEventListener('change', () => searchProgrammes(1));
    }
}

// Run programmes initialization when DOM is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initProgrammesPage);
} else {
    initProgrammesPage();
}
// ========== END NEW CODE ==========