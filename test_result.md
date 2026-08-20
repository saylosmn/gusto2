#====================================================================================================
# START - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================

# THIS SECTION CONTAINS CRITICAL TESTING INSTRUCTIONS FOR BOTH AGENTS
# BOTH MAIN_AGENT AND TESTING_AGENT MUST PRESERVE THIS ENTIRE BLOCK

# Communication Protocol:
# If the `testing_agent` is available, main agent should delegate all testing tasks to it.
#
# You have access to a file called `test_result.md`. This file contains the complete testing state
# and history, and is the primary means of communication between main and the testing agent.
#
# Main and testing agents must follow this exact format to maintain testing data. 
# The testing data must be entered in yaml format Below is the data structure:
# 
## user_problem_statement: {problem_statement}
## backend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.py"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## frontend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.js"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## metadata:
##   created_by: "main_agent"
##   version: "1.0"
##   test_sequence: 0
##   run_ui: false
##
## test_plan:
##   current_focus:
##     - "Task name 1"
##     - "Task name 2"
##   stuck_tasks:
##     - "Task name with persistent issues"
##   test_all: false
##   test_priority: "high_first"  # or "sequential" or "stuck_first"
##
## agent_communication:
##     -agent: "main"  # or "testing" or "user"
##     -message: "Communication message between agents"

# Protocol Guidelines for Main agent
#
# 1. Update Test Result File Before Testing:
#    - Main agent must always update the `test_result.md` file before calling the testing agent
#    - Add implementation details to the status_history
#    - Set `needs_retesting` to true for tasks that need testing
#    - Update the `test_plan` section to guide testing priorities
#    - Add a message to `agent_communication` explaining what you've done
#
# 2. Incorporate User Feedback:
#    - When a user provides feedback that something is or isn't working, add this information to the relevant task's status_history
#    - Update the working status based on user feedback
#    - If a user reports an issue with a task that was marked as working, increment the stuck_count
#    - Whenever user reports issue in the app, if we have testing agent and task_result.md file so find the appropriate task for that and append in status_history of that task to contain the user concern and problem as well 
#
# 3. Track Stuck Tasks:
#    - Monitor which tasks have high stuck_count values or where you are fixing same issue again and again, analyze that when you read task_result.md
#    - For persistent issues, use websearch tool to find solutions
#    - Pay special attention to tasks in the stuck_tasks list
#    - When you fix an issue with a stuck task, don't reset the stuck_count until the testing agent confirms it's working
#
# 4. Provide Context to Testing Agent:
#    - When calling the testing agent, provide clear instructions about:
#      - Which tasks need testing (reference the test_plan)
#      - Any authentication details or configuration needed
#      - Specific test scenarios to focus on
#      - Any known issues or edge cases to verify
#
# 5. Call the testing agent with specific instructions referring to test_result.md
#
# IMPORTANT: Main agent must ALWAYS update test_result.md BEFORE calling the testing agent, as it relies on this file to understand what to test next.

#====================================================================================================
# END - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================



#====================================================================================================
# Testing Data - Main Agent and testing sub agent both should log testing data below this section
#====================================================================================================

user_problem_statement: |
  Gusto Restaurant — production-feeling, multilingual (6 locales), multi-branch (3 branches)
  restaurant website. Slice A (public site) on Next.js App Router + MongoDB. Everything DB-driven.
  Per-branch price overrides embedded on menu items (read-only in slice A). Reservations form ->
  DB with validation against that branch's hours in Asia/Ulaanbaatar. No admin/inbox yet; no PII
  exposure from public endpoints.

backend:
  - task: "GET /api/bootstrap (auto-seed + assembled payload)"
    implemented: true
    working: true
    file: "app/api/[[...path]]/route.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
        - working: "NA"
          agent: "main"
          comment: "Returns { brand, branches[3], categories[6], menuItems[15] }. Auto-seeds on first call if branches empty. Each branch has openingHours/testimonials/gallery attached. MongoDB _id must be stripped from every document. menuItems must include embedded branchOverrides array. Verify counts and that no _id leaks."
        - working: true
          agent: "testing"
          comment: "✅ ALL CHECKS PASSED. Verified: (1) Returns 200 with all required keys (brand, branches, categories, menuItems). (2) Branches count = 3 with correct slugs (seoul-street, white-gate, tenger). (3) Each branch has openingHours, testimonials, gallery arrays attached. (4) Categories count = 6. (5) MenuItems count = 15. (6) All menuItems have branchOverrides array with objects containing branchId, priceOverride, isAvailable, isServed. (7) CRITICAL: NO MongoDB _id fields found anywhere in response (branches, items, nested docs). (8) Brand has all required keys: name, tagline (object), positioning (object), phone, social (object with instagram/facebook)."
  - task: "POST /api/reservations (UB-timezone validation)"
    implemented: true
    working: true
    file: "app/api/[[...path]]/route.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
        - working: "NA"
          agent: "main"
          comment: |
            Validation runs in Asia/Ulaanbaatar. Branch ids: br-seoul-street, br-white-gate, br-tenger.
            Test cases: (1) missing fields (omit name) -> 400 error=MISSING_FIELDS.
            (2) past date e.g. 2020-01-01 20:00 -> 400 error=PAST_TIME.
            (3) br-seoul-street with a clearly FUTURE date at time 08:00 (before its 09:00 open) -> 400 error=BEFORE_OPEN.
            (4) br-seoul-street future date at 20:00 -> 200 success { id, status:'requested', phone }. (closesAt is null so no AFTER_CLOSE).
            (5) br-tenger (no opening hours seeded) future date any time -> 200 success (hours unknown, accepted).
            Also confirm the endpoint NEVER returns lists of reservations / other guests' name+phone.
        - working: true
          agent: "testing"
          comment: "✅ ALL VALIDATION TESTS PASSED. (1) Missing name field -> 400 {error:MISSING_FIELDS} ✓. (2) Past date 2020-01-01 20:00 -> 400 {error:PAST_TIME} ✓. (3) br-seoul-street future date 08:00 (before 09:00 open) -> 400 {error:BEFORE_OPEN} ✓. (4) br-seoul-street future date 20:00 -> 200 {id, status:requested, phone:+976 7733 6969} ✓. (5) br-tenger future date 13:00 (no opening hours) -> 200 success ✓. SECURITY VERIFIED: (a) POST response contains ONLY {id, status, phone} - no other guest data leaked. (b) GET /api/reservations returns 404 - no PII exposure endpoint exists."
  - task: "POST /api/seed (force reseed, idempotent) + GET /api/health"
    implemented: true
    working: true
    file: "app/api/[[...path]]/route.js"
    stuck_count: 0
    priority: "medium"
    needs_retesting: false
    status_history:
        - working: "NA"
          agent: "main"
          comment: "POST /api/seed wipes and reinserts the 7 seed collections (not reservations) and returns { ok:true, seeded:true }. GET /api/health returns { ok:true }. Running seed twice should be safe."
        - working: true
          agent: "testing"
          comment: "✅ ALL TESTS PASSED. (1) GET /api/health -> 200 {ok:true} ✓. (2) POST /api/seed first call -> 200 {ok:true, seeded:true} ✓. (3) POST /api/seed second call (idempotency) -> 200 {ok:true, seeded:true} ✓. (4) GET /api/bootstrap after seed -> correct counts maintained (3 branches, 6 categories, 15 menuItems) ✓. Seed endpoint is safe to call multiple times."

frontend:
  - task: "Public SPA (routing, i18n, retint, menu, reserve)"
    implemented: true
    working: true
    file: "app/page.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
        - working: true
          agent: "main"
          comment: "Verified via screenshots: mn group home (live-status ICU countdown), en Seoul menu (dense 2-col, leader dots, sold-out grey, compare-across-branches pills), ja Tenger branch home (barolo retint + Noto JP + ja->mn address fallback + hours-not-confirmed state). NOT to be re-tested by testing agent without explicit user permission."

metadata:
  created_by: "main_agent"
  version: "1.0"
  test_sequence: 1
  run_ui: false

test_plan:
  current_focus: []
  stuck_tasks: []
  test_all: false
  test_priority: "high_first"

agent_communication:
    - agent: "main"
      message: |
        Slice A backend is ready for testing. Please test the three backend tasks above via the
        public base URL with the /api prefix. Focus on the reservation validation matrix (UB timezone)
        and confirm no PII/reservation lists are returned. Do NOT test the frontend (user will decide).
    - agent: "testing"
      message: |
        Backend testing complete - ALL TESTS PASSED (4/4). Tested via https://gusto-restaurant-hub.preview.emergentagent.com/api.
        
        ✅ GET /api/health - Working correctly
        ✅ GET /api/bootstrap - All validations passed (counts, structure, no _id leaks, nested arrays)
        ✅ POST /api/reservations - All validation scenarios passed (missing fields, past time, before open, success cases, security checks)
        ✅ POST /api/seed - Idempotency verified, health check working
        
        CRITICAL SECURITY VALIDATIONS CONFIRMED:
        - No MongoDB _id fields in any response
        - POST /api/reservations returns only {id, status, phone} - no PII leak
        - GET /api/reservations returns 404 - no public access to reservation lists
        
        All backend APIs are production-ready. No issues found.
