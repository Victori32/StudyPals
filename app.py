import streamlit as st
import os
import time
from utils import get_openai_api_key, load_env
from crewai import Agent, Task, Crew
from crewai_tools import SerperDevTool, ScrapeWebsiteTool, WebsiteSearchTool
from langchain_openai import ChatOpenAI
from crewai import Process

# Configure page
st.set_page_config(
    page_title="StudyPals",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "results" not in st.session_state:
    st.session_state.results = None
if "show_loading" not in st.session_state:
    st.session_state.show_loading = False
if "custom_courses" not in st.session_state:
    st.session_state.custom_courses = []
if "custom_deadlines" not in st.session_state:
    st.session_state.custom_deadlines = []
if "custom_study_times" not in st.session_state:
    st.session_state.custom_study_times = []
if "previous_field" not in st.session_state:
    st.session_state.previous_field = None

# Load environment variables and configure SSL
ssl_context = load_env()
openai_api_key = get_openai_api_key()
os.environ["OPENAI_MODEL_NAME"] = 'gpt-3.5-turbo'

# Main UI
st.title("📚 StudyPals")
st.markdown("""
This application uses AI agents to help you find learning resources and create personalized study plans. 
Fill out the form below to get started.
""")

# Sidebar for inputs
st.sidebar.title("Learning Inputs")

# Field of Study Selector
st.sidebar.subheader("Field of Study")
field_of_study = st.sidebar.selectbox(
    "Select your field of study",
    ["Computer Science", "Biology", "Chemistry", "Geography"]
)

# Reset results when field changes
if st.session_state.previous_field != field_of_study:
    st.session_state.results = None
    st.session_state.show_loading = False
    # Update previous field
    st.session_state.previous_field = field_of_study

# Show currently selected field prominently
st.write(f"## Currently Selected: {field_of_study}")
st.markdown(f"_All resources and study plans will be generated for **{field_of_study}**_")

# Define default values based on selected field
if field_of_study == "Computer Science":
    default_main_course = "Introduction to Computer Science"
    default_topic = "Data Structures and Algorithms"
    default_courses = [
        "Introduction to Computer Science(CS101)", 
        "Web Development(CS102)", 
        "Database Systems(CS301)"
    ]
    default_deadlines = [
        "CS101 Assignment 1 due on April 20, 2025",
        "CS301 Database Project due on April 25, 2025"
    ]
elif field_of_study == "Biology":
    default_main_course = "General Biology"
    default_topic = "Cell Structure and Function"
    default_courses = [
        "General Biology(BIO101)", 
        "Human Anatomy(BIO201)", 
        "Genetics(BIO301)"
    ]
    default_deadlines = [
        "BIO101 Lab Report due on April 18, 2025",
        "BIO301 Genetics Research Paper due on April 30, 2025"
    ]
elif field_of_study == "Chemistry":
    default_main_course = "General Chemistry"
    default_topic = "Chemical Bonding"
    default_courses = [
        "General Chemistry(CHEM101)", 
        "Organic Chemistry(CHEM201)", 
        "Biochemistry(CHEM301)"
    ]
    default_deadlines = [
        "CHEM101 Lab Safety Quiz due on April 15, 2025",
        "CHEM201 Molecular Modeling Project due on April 26, 2025"
    ]
elif field_of_study == "Geography":
    default_main_course = "Introduction to Geography"
    default_topic = "Climate Systems"
    default_courses = [
        "Introduction to Geography(GEO101)", 
        "Physical Geography(GEO201)", 
        "Geographic Information Systems(GEO301)"
    ]
    default_deadlines = [
        "GEO101 Map Analysis due on April 17, 2025",
        "GEO301 GIS Project due on April 29, 2025"
    ]

# Course Information
st.sidebar.subheader("Course Information")
course_name = st.sidebar.text_input("Main Course Name", default_main_course)
current_topic = st.sidebar.text_input("Current Topic", default_topic)

# Helper functions to create agents and tasks
def create_agents():
    content_agent = Agent(
        role="Content curator",
        goal=f"Provide access to a wide range of {field_of_study} learning resources and curate high-quality educational content",
        backstory=(
            f"You are developed to address the growing need \
            for personalized and relevant {field_of_study} learning materials. You use SerperDevTool,\
            WebsiteSearchTool to search for best educational resources and \
            ScrapeWebsiteTool to extract and curate content from trusted sources.\
            You aim to help students find the right {field_of_study} materials to enhance their\
            understanding and performance in their courses."
        ),
        allow_delegation=False,
        verbose=True
    )
    
    study_planning_agent = Agent(
        role="Planning specialist",
        goal=f"Assist students in creating study schedules and deadlines for {field_of_study} courses",
        backstory=(
            f"You are designed to help students manage\
            their time effectively and stay organized in their {field_of_study} studies.\
            You use WebsiteSearchTool to find best practices for study planning\
            and integrates with the course management to sync deadlines and schedules.\
            You aim to help students stay on track and reduce stress\
            by providing a clear and structured plan for {field_of_study} courses."
        ),
        verbose=True
    )
    
    return content_agent, study_planning_agent

def create_tasks(content_agent, study_planning_agent):
    content_agent_task = Task(
        description=(
            f"Find and curate high-quality learning resources for {current_topic} in {field_of_study}. "
            f"You MUST include actual working URLs from educational websites, academic journals, video lectures, "
            f"and other credible sources. Do not fabricate URLs - use real websites with actual content for {current_topic}."
        ),
        expected_output=(
            f"A list of 5-10 high-quality learning resources (articles, videos, tutorials) "
            f"specifically relevant to {current_topic} in {field_of_study}. "
            f"Each resource MUST include: "
            f"1. A descriptive title "
            f"2. A brief 1-2 sentence description explaining what the student will learn "
            f"3. A working URL to the resource (e.g., https://example.com/article). "
            f"4. The format of the resource (video, article, interactive tutorial, etc.). "
            f"Focus on finding resources from credible educational platforms like Coursera, Khan Academy, MIT OpenCourseWare, "
            f"academic journals, university websites and other trusted sources."
        ),
        tools=[SerperDevTool, ScrapeWebsiteTool, WebsiteSearchTool],
        agent=content_agent,
    )
    
    study_agent_task = Task(
        description=(
            f"Create a detailed personalized study schedule for a student studying {field_of_study}, focusing on {current_topic}. "
            f"The schedule should incorporate all the student's courses: {student_courses}. "
            f"Consider these preferred study times: {preferred_study_times}. "
            f"And account for these deadlines: {important_deadlines}. "
            f"Create a comprehensive day-by-day, hour-by-hour plan. "
            f"IMPORTANT: For each study session in the plan, include links to specific online courses, video lectures, "
            f"tutorials, practice exercises, or textbook chapters that the student should use during that session. "
            f"DO NOT invent or fabricate URLs. ONLY use real, functioning links to actual educational resources "
            f"that you have verified exist and are accessible. Search for these resources using your tools."
        ),
        expected_output=(
            f"A comprehensive study plan that includes: "
            f"1. A DAILY SCHEDULE: Provide a detailed day-by-day schedule for at least 2 weeks, with specific time slots allocated to each course. "
            f"2. TOPIC BREAKDOWN: For each study session, specify exactly which topics and subtopics to cover from {current_topic} and other courses. "
            f"3. PREPARATION TIMELINE: Create a countdown timeline for all upcoming deadlines, with specific milestones to complete before each deadline. "
            f"4. STUDY TECHNIQUES: Recommend specific study techniques for different types of material in {field_of_study}. "
            f"5. LINKED RESOURCES: For EACH study session, include at least 1-2 specific links to relevant educational resources such as: "
            f"   - Links to specific video lectures (YouTube, Coursera, Khan Academy) "
            f"   - Links to online textbooks, tutorials, or documentation "
            f"   - Links to practice exercises or problem sets "
            f"   - Links to interactive tools or simulations when appropriate "
            f"FORMAT EACH LINK using Markdown format: [Resource Name](URL). Use real, working URLs to legitimate educational resources. "
            f"Double-check all URLs to ensure they are correct and accessible. "
            f"The plan should be highly structured, practical, and ready to implement immediately, with each study session having linked resources."
        ),
        tools=[SerperDevTool, WebsiteSearchTool],
        agent=study_planning_agent,
    )
    
    return content_agent_task, study_agent_task

def create_crew(content_agent, study_planning_agent, content_agent_task, study_agent_task):
    educational_crew = Crew(
        agents=[content_agent, study_planning_agent],
        tasks=[content_agent_task, study_agent_task],
        manager_llm=ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7),
        process=Process.hierarchical,
        verbose=True
    )
    
    return educational_crew

# Custom Course Manager
st.sidebar.subheader("Student Courses")
with st.sidebar.expander("Manage Courses", expanded=False):
    # Default courses
    for i, course in enumerate(default_courses):
        st.checkbox(f"Course {i+1}", value=True, key=f"default_course_{i}")
        if st.session_state[f"default_course_{i}"]:
            st.text_input(f"Course {i+1} Details", value=course, key=f"default_course_details_{i}")

    # Custom courses
    st.subheader("Add Custom Courses")
    new_course_name = st.text_input("New Course Name")
    new_course_code = st.text_input("New Course Code")
    
    if st.button("Add Course"):
        if new_course_name and new_course_code:
            new_course = f"{new_course_name}({new_course_code})"
            st.session_state.custom_courses.append(new_course)
            st.success(f"Added: {new_course}")
        else:
            st.warning("Please enter both course name and code")
    
    # Display custom courses
    if st.session_state.custom_courses:
        st.subheader("Your Custom Courses")
        for i, course in enumerate(st.session_state.custom_courses):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.text_input(f"Custom Course {i+1}", value=course, key=f"custom_course_{i}")
            with col2:
                if st.button("Remove", key=f"remove_course_{i}"):
                    st.session_state.custom_courses.pop(i)
                    st.rerun()

# Compile all selected courses
selected_courses = []
for i, course in enumerate(default_courses):
    if st.session_state.get(f"default_course_{i}", False):
        selected_courses.append(st.session_state.get(f"default_course_details_{i}", course))
selected_courses.extend(st.session_state.custom_courses)
student_courses = ", ".join(selected_courses)

# Study Times
st.sidebar.subheader("Study Preferences")
with st.sidebar.expander("Manage Study Times", expanded=False):
    # Default study times
    default_times = ["2 hours in the morning", "2 hours in the evening"]
    for i, time in enumerate(default_times):
        st.checkbox(f"Time Slot {i+1}", value=True, key=f"default_time_{i}")
        if st.session_state[f"default_time_{i}"]:
            st.text_input(f"Time Slot {i+1} Details", value=time, key=f"default_time_details_{i}")
    
    # Custom study times
    st.subheader("Add Custom Study Times")
    new_study_time = st.text_input("New Study Time (e.g., 1 hour after lunch)")
    
    if st.button("Add Study Time"):
        if new_study_time:
            st.session_state.custom_study_times.append(new_study_time)
            st.success(f"Added: {new_study_time}")
        else:
            st.warning("Please enter a study time")
    
    # Display custom study times
    if st.session_state.custom_study_times:
        st.subheader("Your Custom Study Times")
        for i, time in enumerate(st.session_state.custom_study_times):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.text_input(f"Custom Time {i+1}", value=time, key=f"custom_time_{i}")
            with col2:
                if st.button("Remove", key=f"remove_time_{i}"):
                    st.session_state.custom_study_times.pop(i)
                    st.rerun()

# Compile all selected study times
selected_times = []
for i, time in enumerate(default_times):
    if st.session_state.get(f"default_time_{i}", False):
        selected_times.append(st.session_state.get(f"default_time_details_{i}", time))
selected_times.extend(st.session_state.custom_study_times)
preferred_study_times = ", ".join(selected_times)

# Deadlines
st.sidebar.subheader("Important Deadlines")
with st.sidebar.expander("Manage Deadlines", expanded=False):
    # Default deadlines
    for i, deadline in enumerate(default_deadlines):
        st.checkbox(f"Deadline {i+1}", value=True, key=f"default_deadline_{i}")
        if st.session_state[f"default_deadline_{i}"]:
            st.text_input(f"Deadline {i+1} Details", value=deadline, key=f"default_deadline_details_{i}")
    
    # Custom deadlines
    st.subheader("Add Custom Deadline")
    new_deadline_course = st.text_input("Course Code")
    new_deadline_task = st.text_input("Task (e.g., Assignment, Exam)")
    new_deadline_date = st.date_input("Due Date")
    
    if st.button("Add Deadline"):
        if new_deadline_course and new_deadline_task:
            new_deadline = f"{new_deadline_course} {new_deadline_task} due on {new_deadline_date.strftime('%B %d, %Y')}"
            st.session_state.custom_deadlines.append(new_deadline)
            st.success(f"Added: {new_deadline}")
        else:
            st.warning("Please enter both course code and task")
    
    # Display custom deadlines
    if st.session_state.custom_deadlines:
        st.subheader("Your Custom Deadlines")
        for i, deadline in enumerate(st.session_state.custom_deadlines):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.text_input(f"Custom Deadline {i+1}", value=deadline, key=f"custom_deadline_{i}")
            with col2:
                if st.button("Remove", key=f"remove_deadline_{i}"):
                    st.session_state.custom_deadlines.pop(i)
                    st.rerun()

# Compile all selected deadlines
selected_deadlines = []
for i, deadline in enumerate(default_deadlines):
    if st.session_state.get(f"default_deadline_{i}", False):
        selected_deadlines.append(st.session_state.get(f"default_deadline_details_{i}", deadline))
selected_deadlines.extend(st.session_state.custom_deadlines)
important_deadlines = ", ".join(selected_deadlines)

# Other options
news_impact = st.sidebar.checkbox("Consider Recent Developments", value=True)

# Collect inputs
learning_inputs = {
    'Field of study': field_of_study,
    'Course name': course_name,
    'Current Topic': current_topic,
    'Student courses': student_courses,
    'Preferred Study times': preferred_study_times,
    'Important deadlines': important_deadlines,
    'news_impact_consideration': news_impact
}

# Create a single comprehensive view
st.header(f"{field_of_study} Comprehensive Learning Hub")

def run_educational_crew():
    # Display a field-specific message
    st.info(f"Generating content specifically for {field_of_study} - {current_topic}")
    
    # Create agents, tasks, and crew
    content_agent, study_planning_agent = create_agents()
    content_agent_task, study_agent_task = create_tasks(content_agent, study_planning_agent)
    educational_crew = create_crew(content_agent, study_planning_agent, content_agent_task, study_agent_task)
    
    # Run the crew with the collected inputs
    with st.spinner(f"AI agents are working on your {field_of_study} request. This may take a few minutes..."):
        st.session_state.show_loading = True
        result = educational_crew.kickoff(inputs=learning_inputs)
        st.session_state.results = result
        st.session_state.show_loading = False
    
    st.rerun()

if st.sidebar.button(f"Generate {field_of_study} Results"):
    if not st.session_state.show_loading:
        run_educational_crew()

if st.session_state.results:
    col1, col2 = st.columns([1, 3])
    
    resources_section = st.session_state.results.split("Study Schedule:")[0] if "Study Schedule:" in st.session_state.results else st.session_state.results
    
    with col2:
        st.subheader(f"{field_of_study} Complete Learning Package")
        
        st.markdown("---")
        
        st.subheader(f"📚 Learning Resources and Study Plan")
        
        st.info("All links below are clickable and will open in a new tab. Click on any resource to access it directly.")
        
        st.markdown(resources_section, unsafe_allow_html=True)
        
        st.markdown("---")
        
        has_study_plan = "Study Schedule:" in st.session_state.results
        
        if has_study_plan:
            study_plan_section = "Study Schedule:" + st.session_state.results.split("Study Schedule:")[1]
            st.markdown(study_plan_section, unsafe_allow_html=True)
            
            st.info("The study plan includes direct links to recommended learning resources for each session. Click any link to access the resource.")
        else:
            st.info("Your learning resources are ready!")

else:
    st.info(f"Click 'Generate {field_of_study} Results' to get a comprehensive learning package for {current_topic}.")
    
    st.subheader("What You'll Get")
    
    # Resources preview
    st.markdown("### 📚 Learning Resources and 📅 Study Plan")
    st.markdown("• Hand-picked educational materials specific to your topic")
    st.markdown("• Links to tutorials, videos, articles, and academic papers")
    st.markdown("• Curated resources from trusted educational platforms")
    st.markdown("• Detailed day-by-day schedule customized to your preferences")
    st.markdown("• Topic breakdowns for efficient learning")
    st.markdown("• Deadline preparation timeline with specific milestones")
    st.markdown("• Recommended study techniques for your field")

# Footer
st.sidebar.markdown("---")
st.sidebar.caption("Powered by CrewAI and OpenAI") 