import streamlit as st
import os
import subprocess
from PIL import Image

# --------------------------------------------
# PAGE CONFIG
# --------------------------------------------
st.set_page_config(page_title="Placement Database Management System 🎓",
                   layout="wide",
                   page_icon="🎓")

# --------------------------------------------
# HEADER WITH LOGO
# --------------------------------------------
col1, col2 = st.columns([1, 6])
with col1:
    try:
        logo = Image.open("logo.jpg")  # ensure logo.jpg is in same folder
        st.image(logo, width=80)
    except:
        st.write("")  # ignore if not found
with col2:
    st.markdown("<h2 style='margin-top: 10px;'>Placement Database Management System 🎓</h2>",
                unsafe_allow_html=True)

# --------------------------------------------
# BACKEND COMMAND RUNNER (NEW)
# --------------------------------------------
def run_backend(*args):
    result = subprocess.run(["./backend.exe", *map(str, args)], capture_output=True, text=True)
    return result.stdout.strip()

def apply_job_backend(student_roll, jobid):
    out = run_backend("apply_job", student_roll, jobid)
    return out

def post_job_backend(company, title, ctc, criteria):
    out = run_backend("post_job", company, title, ctc, criteria)
    return out


def get_jobs_from_backend():
    out = run_backend("list_jobs")
    lines = out.split("\n")
    jobs = []

    if len(lines) > 1:
        headers = lines[0].split("\t")
        for row in lines[1:]:
            if row.strip():
                values = row.split("\t")
                jobs.append(dict(zip(headers, values)))

    return jobs

def get_applications_from_backend():
    path = "data/applications.txt"
    if not os.path.exists(path):
        return []

    applications = []
    with open(path, "r") as f:
        for line in f:
            parts = line.strip().split(",")
            if len(parts) == 3:
                applications.append({
                    "roll": parts[0],
                    "jobid": parts[1],
                    "status": parts[2]
                })
    return applications

# --------------------------------------------
# OLD FUNCTIONS (FOR LOGIN & REGISTER)
# --------------------------------------------
def save_user(role, username, password):
    os.makedirs("data", exist_ok=True)
    file = f"data/{role}_users.txt"
    with open(file, "a") as f:
        f.write(f"{username},{password}\n")

def validate_user(role, username, password):
    file = f"data/{role}_users.txt"
    if not os.path.exists(file):
        return False
    with open(file, "r") as f:
        for line in f:
            u, p = line.strip().split(",")
            if u == username and p == password:
                return True
    return False

def update_password(role, username, old_password, new_password):
    file = f"data/{role}_users.txt"
    if not os.path.exists(file):
        return False
    updated = False
    with open(file, "r") as f:
        lines = f.readlines()
    with open(file, "w") as f:
        for line in lines:
            u, p = line.strip().split(",")
            if u == username and p == old_password:
                f.write(f"{u},{new_password}\n")
                updated = True
            else:
                f.write(line)
    return updated

# --------------------------------------------
# MAIN NAVIGATION
# --------------------------------------------
menu = ["Login", "Sign Up", "About"]
choice = st.sidebar.selectbox("Main Menu", menu)

# --------------------------------------------
# SIGN UP PAGE
# --------------------------------------------
if choice == "Sign Up":
    st.subheader("🔐 Create an Account")
    role = st.selectbox("Select Role", ["Student", "Company", "Placement Officer"])
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Register"):
        if username and password:
            save_user(role, username, password)
            st.success(f"✅ Account created successfully for {username} ({role})")
        else:
            st.warning("Please fill all fields!")

# --------------------------------------------
# LOGIN PAGE & DASHBOARDS
# --------------------------------------------
elif choice == "Login":

    if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
        st.subheader("🔑 Login to Your Account")

        role = st.selectbox("Role", ["Student", "Company", "Placement Officer"])
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if validate_user(role, username, password):
                st.session_state["logged_in"] = True
                st.session_state["role"] = role
                st.session_state["username"] = username
                st.success(f"Welcome, {username} ({role})!")
                st.rerun()
            else:
                st.error("Invalid username or password!")

    else:
        st.sidebar.markdown("---")
        st.sidebar.subheader(f"Welcome, {st.session_state['username']} 👋")
        role = st.session_state["role"]

        # ==========================================================
        # STUDENT DASHBOARD
        # ==========================================================
        if role == "Student":
            section = st.sidebar.radio("📚 Student Dashboard",
                                       ["Home", "View Jobs", "Apply for Job", "Profile", "Settings"],
                                       index=0)

            st.sidebar.markdown("---")
            if st.sidebar.button("🚪 Logout"):
                st.session_state.clear()
                st.rerun()

            if section == "Home":
                st.header("🎯 Student Dashboard — Home")
                st.success(f"Welcome, {st.session_state['username']}!")

            elif section == "View Jobs":
                st.header("💼 Available Job Listings")
                
                jobs = get_jobs_from_backend()

                if not jobs:
                    st.warning("No jobs posted yet.")
                else:
                    st.table(jobs)

            elif section == "Apply for Job":
                st.header("📝 Apply for Jobs")

                jobs = get_jobs_from_backend()
                if not jobs:
                    st.warning("No jobs available to apply.")
                else:
                    job_ids = [job["jobid"] for job in jobs]
                    selected_job = st.selectbox("Select Job ID to Apply", job_ids)

                    if st.button("Apply Now ✅"):
                        student = st.session_state["username"]   # username = roll number
                        result = apply_job_backend(student, selected_job)
                        st.success(f"Application submitted for Job ID {selected_job} 🎉")

            elif section == "Profile":
                st.header("👤 Student Profile")

                roll = st.session_state["username"]  # student username = roll number

                st.subheader("Add / Update Profile")
                name = st.text_input("Enter Name")
                cgpa = st.text_input("Enter CGPA")
                backlog = st.selectbox("Backlog", ["0", "1"])

                if st.button("Save Profile ✅"):
                    run_backend("add_student", roll, name, cgpa, backlog)
                    st.success("✅ Profile Saved Successfully!")

                st.subheader("View My Profile")
                if st.button("Load My Profile"):
                    data = run_backend("list_students")  # temporary viewing method
                    with open("data/students.txt", "r") as f:
                        found = False
                        for line in f:
                            fields = line.strip().split(",")
                            if fields[0] == roll:
                                st.write(f"**Roll:** {fields[0]}")
                                st.write(f"**Name:** {fields[1]}")
                                st.write(f"**CGPA:** {fields[2]}")
                                st.write(f"**Backlogs:** {fields[3]}")
                                found = True
                                break
                        if not found:
                            st.warning("No profile found. Please save profile first.")

            elif section == "Settings":
                st.header("⚙️ Account Settings")
                old = st.text_input("Enter Current Password", type="password")
                new = st.text_input("Enter New Password", type="password")
                confirm = st.text_input("Confirm New Password", type="password")
                if st.button("Update Password"):
                    if new == confirm:
                        if update_password(role, st.session_state["username"], old, new):
                            st.success("✅ Password updated successfully!")
                        else:
                            st.error("❌ Incorrect old password.")
                    else:
                        st.warning("Passwords do not match!")

        # ==========================================================
        # COMPANY DASHBOARD
        # ==========================================================
        elif role == "Company":
            section = st.sidebar.radio("🏢 Company Dashboard",
                                       ["Home", "Post Job", "View Applications", "Shortlist", "Settings"],
                                       index=0)

            st.sidebar.markdown("---")
            if st.sidebar.button("🚪 Logout"):
                st.session_state.clear()
                st.rerun()

            st.header(f"🏢 Company Dashboard ({st.session_state['username']})")

            if section == "Post Job":
                st.header("📋 Post New Job")

                company = st.session_state["username"]  # company name from login
                title = st.text_input("Job Title")
                ctc = st.text_input("Package / CTC (e.g., 6LPA)")
                criteria = st.text_input("Eligibility Criteria (e.g., CGPA>7)")

                if st.button("Post Job ✅"):
                    if title and ctc and criteria:
                        post_job_backend(company, title, ctc, criteria)
                        st.success("✅ Job Posted Successfully!")
                    else:
                        st.warning("⚠️ Please fill all fields before posting.")

            if section == "View Applications":
                st.header("📂 View Applications")

                apps = get_applications_from_backend()

                if not apps:
                    st.warning("No applications received yet.")
                else:
                    st.table(apps)
            
            if section == "Shortlist":
                st.header("✅ Shortlist Applicants")

                apps = get_applications_from_backend()

                if not apps:
                    st.warning("No applications found.")
                else:
                    for i, app in enumerate(apps):   # <-- Add enumerate()
                        col1, col2, col3 = st.columns([3, 3, 2])
                        col1.write(f"**Roll:** {app['roll']}")
                        col2.write(f"**Job ID:** {app['jobid']}")
                        # ✅ Guaranteed unique key using index + roll + jobid
                        unique_key = f"shortlist_{i}_{app['roll']}_{app['jobid']}"
                        if col3.button("Shortlist ✅", key=unique_key):
                            run_backend("shortlist", app['roll'], app['jobid'])
                            st.success(f"🎉 Shortlisted {app['roll']} for Job {app['jobid']}")

        # ==========================================================
        # PLACEMENT OFFICER DASHBOARD
        # ==========================================================
        elif role == "Placement Officer":
            section = st.sidebar.radio("📊 Officer Dashboard",
                                    ["Home", "Manage Students", "Manage Companies", "Reports", "Process Placements", "Settings"],
                                    index=0)

            st.sidebar.markdown("---")
            if st.sidebar.button("🚪 Logout"):
                st.session_state.clear()
                st.rerun()

            # -------- Home ----------
            if section == "Home":
                st.header("📊 Placement Overview Dashboard")
                st.success(f"Welcome, {st.session_state['username']}!")

                # Summary counts
                student_data = run_backend("list_students")
                company_data = run_backend("list_companies")
                jobs_data = run_backend("list_jobs")

                st.write("### 🎓 Registered Students:")
                st.text(student_data)

                st.write("### 🏢 Registered Companies:")
                st.text(company_data)

                st.write("### 💼 Job Listings:")
                st.text(jobs_data)

            # -------- Manage Students ----------
            elif section == "Manage Students":
                st.header("👨‍🎓 Manage Students")

                st.subheader("📋 Student List")
                students = run_backend("list_students")
                st.text(students)

                st.markdown("---")
                st.subheader("➕ Add Student")
                roll = st.text_input("Roll Number")
                name = st.text_input("Name")
                cgpa = st.text_input("CGPA")
                backlog = st.selectbox("Backlog", ["0", "1"])
                if st.button("Add Student ✅"):
                    run_backend("add_student", roll, name, cgpa, backlog)
                    st.success("✅ Student Added!")

            # -------- Manage Companies ----------
            elif section == "Manage Companies":
                st.header("🏢 Manage Companies")

                st.subheader("📋 Company List")
                companies = run_backend("list_companies")
                st.text(companies)

                st.markdown("---")
                st.subheader("➕ Add Company")
                cname = st.text_input("Company Name")
                criteria = st.text_input("Eligibility Criteria")
                pkg = st.text_input("Package (CTC)")
                if st.button("Add Company ✅"):
                    run_backend("post_job", cname, "NA", pkg, criteria)  # reuse backend j
                    st.success("✅ Company Added!")

            elif section == "Reports":
                st.header("📈 Placement Reports")
                st.info("Using backend merge sort + data summaries")
                run_backend("reports")

                # -------- Process Placements ----------
            elif section == "Process Placements":
                st.header("✅ Finalize Shortlisted Candidates")
                st.warning("This will convert all shortlisted to *Placed* status.")
                if st.button("Process Placement Queue"):
                    out = run_backend("process_queue")
                    st.success("🎉 All shortlisted candidates marked as Placed!")

                # -------- Settings ----------
            elif section == "Settings":
                st.header("⚙️ Account Settings")
                old = st.text_input("Current Password", type="password")
                new = st.text_input("New Password", type="password")
                confirm = st.text_input("Confirm Password", type="password")
                if st.button("Update Password"):
                    if new == confirm:
                        run_backend("change_password", "Placement Officer", st.session_state["username"], old, new)
                        st.success("✅ Password Updated!")
                    else:
                        st.warning("⚠️ Passwords do not match!")

# --------------------------------------------
# ABOUT PAGE
# --------------------------------------------
elif choice == "About":
    st.header("📘 About the Project")
    st.markdown("""
    The **Placement Database Management System (PDMS)** helps manage campus placements efficiently.
    """)

st.sidebar.markdown("---")
st.sidebar.caption("Developed by Placement Achievers — Dipanshu, Vidhit, Akshat, Ayush © 2025")
