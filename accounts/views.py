from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Profile
from .models import SurgeryActivity, SurgeryActivityDetail
from .models import AnaesthesiaActivity, AnaesthesiaDetail
from .models import UpperGIActivity, UpperGIDetail
from .models import EmergencyTraumaActivity, EmergencyTraumaDetail
from .models import GSColorectalActivity, GSColorectalDetail
from django.db.models import Sum, Case, When, IntegerField
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP


# =============================================
# HELPER FUNCTION - AUTO CALCULATE FORMULA
# =============================================
def calculate_domain_scores(performances, target, weight):
    """
    ✅ FORMULA:
    - score = (performances / target) × 100  (percentage)
    - weighted_score = (performances / target) × weight
    - index = performances / target  (ratio)
    
    Returns: (score, weighted_score, index)
    """
    try:
        performances_d = Decimal(str(performances))
    except:
        performances_d = Decimal('0')
    
    try:
        target_d = Decimal(str(target))
    except:
        target_d = Decimal('0')
    
    try:
        weight_d = Decimal(str(weight))
    except:
        weight_d = Decimal('0')
    
    if target_d > 0:
        score_d = (performances_d / target_d) * Decimal('100')
        wscore_d = (performances_d / target_d) * weight_d
        index_d = performances_d / target_d
    else:
        score_d = Decimal('0')
        wscore_d = Decimal('0')
        index_d = Decimal('0')
    
    score_f = float(score_d.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
    wscore_f = float(wscore_d.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
    index_f = float(index_d.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
    
    return score_f, wscore_f, index_f


# =============================================
# AUTHENTICATION & MAIN PAGES
# =============================================
def main(request):
    return render(request, 'accounts/main.html')


def journey(request):
    return render(request, 'accounts/journey.html')


@login_required
def register_user(request):
    if not request.user.is_superuser:
        return redirect('fraternity')

    if request.method == "POST":
        full_name = request.POST.get('full_name')
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        bidang = request.POST.get('bidang')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('register_user')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username is already in use.")
            return redirect('register_user')

        user = User.objects.create_user(username=username, password=password)
        Profile.objects.create(user=user, full_name=full_name, bidang_pembedahan=bidang)

        messages.success(request, "User has been successfully registered!")
        return redirect('register_user')

    return render(request, 'accounts/register_user.html')


def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('register_user')
            else:
                return redirect('fraternity')
        else:
            messages.error(request, "Incorrect username or password")
    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def fraternity(request):
    context = {
        # Menggunakan SurgeryActivity (dengan ejaan yang tepat)
        'latest_gs': SurgeryActivity.objects.filter(fraternity="General Surgery").order_by('-year', '-period').first(),
        'latest_gsbreast_endocrine': SurgeryActivity.objects.filter(fraternity="General Surgery Breast and Endocrine").order_by('-year', '-period').first(),
        'latest_gsvascular': SurgeryActivity.objects.filter(fraternity="General Surgery Vascular").order_by('-year', '-period').first(),
        'latest_gshepatobiliary': SurgeryActivity.objects.filter(fraternity="General Surgery Hepatobiliary").order_by('-year', '-period').first(),
        'latest_gsthoracic': SurgeryActivity.objects.filter(fraternity="General Surgery Thoracic").order_by('-year', '-period').first(),
        'latest_gstrauma': SurgeryActivity.objects.filter(fraternity="General Surgery Trauma").order_by('-year', '-period').first(),
        'latest_ophthalmology': SurgeryActivity.objects.filter(fraternity="Ophthalmology").order_by('-year', '-period').first(),
        'latest_orthopaedic': SurgeryActivity.objects.filter(fraternity="Orthopaedic").order_by('-year', '-period').first(),
        'latest_neurosurgery': SurgeryActivity.objects.filter(fraternity="Neurosurgery").order_by('-year', '-period').first(),
        'latest_urology': SurgeryActivity.objects.filter(fraternity="Urology").order_by('-year', '-period').first(),
        'latest_paediatric': SurgeryActivity.objects.filter(fraternity="Paediatric Surgery").order_by('-year', '-period').first(),
        'latest_cardiothoracic': SurgeryActivity.objects.filter(fraternity="Cardiothoracic Surgery").order_by('-year', '-period').first(),
        'latest_obstetrics_gynaecology': SurgeryActivity.objects.filter(fraternity="Obstetrics & Gynaecology").order_by('-year', '-period').first(),
        'latest_otorhinolaryngology': SurgeryActivity.objects.filter(fraternity="Otorhinolaryngology").order_by('-year', '-period').first(),
        'latest_plastic_reconstructive': SurgeryActivity.objects.filter(fraternity="Plastic And Reconstructive Surgery").order_by('-year', '-period').first(),
        'latest_oral_maxillofacial': SurgeryActivity.objects.filter(fraternity="Oral Maxillofacial Surgery").order_by('-year', '-period').first(),
        'latest_public_health': SurgeryActivity.objects.filter(fraternity="Public Health").order_by('-year', '-period').first(),
        'latest_family_medicine': SurgeryActivity.objects.filter(fraternity="Family Medicine").order_by('-year', '-period').first(),
        
        # Menggunakan Model/Jadual Khas
        'latest_gscolorectal': GSColorectalActivity.objects.order_by('-year', '-period').first(),
        'latest_upper_gi': UpperGIActivity.objects.order_by('-year', '-period').first(),
        'latest_anaesthesia': AnaesthesiaActivity.objects.order_by('-year', '-period').first(),
        'latest_emergency_trauma': EmergencyTraumaActivity.objects.order_by('-year', '-period').first(),
    }

    return render(request, 'accounts/fraternity.html', context)


# =============================================
# GENERAL SURGERY
# =============================================
@login_required
def general_surgery(request):
    return render(request, 'accounts/general_surgery.html')


@login_required
def general_surgery_activities(request):
    year = datetime.now().year
    activities = SurgeryActivity.objects.filter(
        fraternity="General Surgery",
        year=year
    ).annotate(
        period_order=Case(
            When(period='Jan-Jun', then=1),
            When(period='Jul-Dec', then=2),
            default=3,
            output_field=IntegerField()
        )
    ).order_by('period_order')

    return render(request, "accounts/general_surgery_activities.html", {
        "activities": activities,
        "year": year,
    })


@login_required
def add_gs_activity(request):
    profile = getattr(request.user, 'profile', None)
    
    # ✅ STRICT CHECK (superadmin bypasses)
    if not request.user.is_superuser and (not profile or profile.bidang_pembedahan != 'GENERAL SURGERY'):
        messages.error(request, "You do not have permission to add this activity.")
        return redirect("general_surgery_activities")
    
    year = datetime.now().year
    existing = SurgeryActivity.objects.filter(fraternity="General Surgery", year=year).count()

    if existing == 0:
        period = "Jan-Jun"
    elif existing == 1:
        period = "Jul-Dec"
    else:
        messages.error(request, "The activities for this year are already complete.")
        return redirect("general_surgery_activities")

    activity, created = SurgeryActivity.objects.get_or_create(
        fraternity="General Surgery",
        year=year,
        period=period
    )
    activity.users.add(request.user)
    messages.success(request, f"You have been added to the activity {period} {year}.")
    return redirect("general_surgery_activities")


@login_required
def form_gs(request, activity_id):
    profile = getattr(request.user, 'profile', None)
    
    # ✅ STRICT CHECK (superadmin bypasses)
    if not request.user.is_superuser and (not profile or profile.bidang_pembedahan != 'GENERAL SURGERY'):
        messages.error(request, "You do not have permission to access this form.")
        return redirect('general_surgery_activities')
    
    activity = get_object_or_404(SurgeryActivity, id=activity_id)

    structure_domains = [
        "National surgical plan policy integration (Aligns surgical services with national health priorities and legislation)",
        "National surgical plan policy integration (Ensures standardized surgical practice across all health facility levels)",
        "Credentialing of minor procedures (Verifies competency of providers performing minor surgical interventions safely)",
        "Credentialing, privileging, quality assurance (Maintains safety and accountability of all surgical practitioners)",
        "Mobile units (Extends surgical access to remote and underserved communities)",
        "District hospitals with minor OR (Provides essential surgical capacity at district-level facilities)",
        "Fully equipped surgical theatres, ICUs (Enables complex and high-acuity surgical procedures safely)",
        "Basic resuscitation kits (Supports emergency stabilization before and after surgical procedures)",
        "Essential surgical/anaesthesia equipment (Ensures availability of core tools for safe surgical and anaesthetic care)",
        "Advanced diagnostic, surgical, anaesthetic equipment (Supports complex case management with accurate diagnostic capability)",
        "Health posts (Serves as first point of contact for surgical screening and referral)",
        "Public Health Specialist, trained community health workers (Supports population-level identification and referral of surgical conditions)",
        "Family Medicine Specialist, General Practitioners (Provides primary-level surgical assessment and timely referral)",
        "Specialists — surgeons, anaesthesiologists, intensivists (Delivers complex and specialized surgical care)",
        "Specific surgical care allocation (Ensures resources are directed to appropriate levels of surgical need)",
        "Specific surgical care allocation (Supports equitable distribution of surgical resources across facilities)",
        "According to activity code (Standardizes documentation and tracking of surgical activities)",
        "Referral tracking, mobile data collection (Enables monitoring of referral pathways and patient movement)",
        "Digital patient records, referral logs (Improves continuity of care through accurate and accessible documentation)",
        "EHRs, surgical registries, POMR tracking systems (Supports comprehensive monitoring and quality improvement of surgical outcomes)"
    ]
    
    process_domains = [
        "Screening & Referral (Identifies patients needing surgical care and routes them appropriately)",
        "Community education, identification of surgical conditions (Empowers communities to seek timely surgical care)",
        "Initial diagnosis and referral (Ensures timely recognition and escalation of surgical conditions)",
        "Multidisciplinary case review and management (Promotes collaborative decision-making for complex surgical cases)",
        "Preoperative Care (Optimizes patient readiness and safety before surgery)",
        "Health education, basic optimization — nutrition, infection prevention (Prepares patients for safer surgical outcomes through lifestyle and education)",
        "Basic investigations, stabilization (Ensures patient is medically prepared and stable for safe surgery)",
        "Pre-op optimization — labs, imaging, specialist consults (Reduces intraoperative risk through thorough pre-surgical assessment)",
        "Communication & Consent (Ensures patients are informed and agree to planned surgical procedures)",
        "Basic awareness (Provides essential information about surgical procedures and expected outcomes)",
        "Informed consent for minor procedures (Ensures patient rights and safety are upheld before minor surgery)",
        "Shared decision-making, risk discussion (Empowers patients to participate meaningfully in their care choices)",
        "Intraoperative - Surgical Safety (Minimizes intraoperative risks through adherence to established safety protocols)",
        "Minor surgical procedures with WHO checklist adherence (Reduces preventable surgical errors through systematic verification)",
        "Full adherence to WHO Surgical Safety Checklist, time-out, sign-out (Prevents wrong-site and wrong-patient surgical errors)",
        "Intraoperative - Anaesthesia Safety (Ensures safe anaesthetic management throughout the surgical procedure)",
        "Local anaesthesia, basic airway management (Supports safe anaesthesia delivery for minor surgical interventions)",
        "ASA classification, anaesthesia protocols, difficult airway algorithm (Guides risk-appropriate anaesthetic management for all patients)",
        "POMR Monitoring (Tracks postoperative outcomes to identify complications and drive improvement)",
        "Not applicable directly (Baseline indicator not directly measured at this level of care)",
        "Referral data for outcomes (Tracks patient outcomes following referral for surgical care)",
        "Formal POMR audit — death within 30 days of surgery (Identifies preventable surgical mortality through structured case review)",
        "Infection Prevention (Reduces surgical site infections and hospital-acquired complications)",
        "Hygiene education (Promotes safe hygiene practices among patients and clinical staff)",
        "Sterilization of instruments (Prevents surgical infections through proper instrument decontamination)",
        "Infection control team, antibiotic prophylaxis protocols (Systematically reduces infection risk in surgical environments)"
    ]

    outcome_domains = [
        "Reduced delays via referral (Measures effectiveness of referral systems in ensuring timely surgical care)",
        "Improved early detection and access (Tracks progress in identifying and reaching patients with surgical needs earlier)",
        "Comprehensive and timely surgical care (Evaluates completeness and speed of surgical service delivery)",
        "Low-complication minor surgeries (Reflects quality and safety of minor surgical procedures performed)",
        "Reduced adverse events, compliance with safety protocols (Monitors reduction of preventable harm through safety adherence)",
        "Monitor referral outcomes (Tracks the success rate and appropriateness of surgical referral pathways)",
        "Measured and reduced through quality improvement (Demonstrates ongoing reduction in surgical complications via QI initiatives)",
        "Community trust and education (Assesses community confidence in and knowledge of surgical services)",
        "Measured and reduced through quality improvement (Tracks improvement in specific surgical outcome metrics over time)",
        "Community trust and education (Reflects public awareness and satisfaction with available surgical care)",
        "Satisfaction with minor care & referral (Captures patient experience with minor surgery and referral services)",
        "Measured through PROMs and PREMs (Uses patient-reported measures to assess health and experience outcomes)",
        "Reaches rural and underserved (Evaluates equity of surgical service access for marginalized populations)",
        "Bridging gap to higher-level care (Measures effectiveness in connecting patients to specialized surgical services)",
        "Equitable care regardless of socioeconomic status (Tracks fairness in surgical care access and outcomes across all patient groups)"
    ]

    details = SurgeryActivityDetail.objects.filter(activity=activity)
    detail_dict = {}
    for d in details:
        key = f"{d.category}_{d.domain}"
        detail_dict[key] = {
            "performances": d.performances_value,
            "target": d.target,
            "weight": d.weight,
            "score": d.score,
            "wscore": d.weighted_score,
            "index": d.index
        }

    if request.method == "POST":
        SurgeryActivityDetail.objects.filter(activity=activity).delete()

        def save_category(category_name, domains):
            total = Decimal('0')
            for i, domain in enumerate(domains, start=1):
                performances = request.POST.get(f"{category_name}_performances_{i}", "0")
                target = request.POST.get(f"{category_name}_target_{i}", "0")
                weight = request.POST.get(f"{category_name}_weight_{i}", "0")

                score_f, wscore_f, index_f = calculate_domain_scores(performances, target, weight)

                SurgeryActivityDetail.objects.create(
                    activity=activity,
                    category=category_name,
                    domain=domain,
                    performances_value=int(performances) if performances else 0,
                    target=int(target) if target else 0,
                    weight=float(weight) if weight else 0,
                    score=score_f,
                    weighted_score=wscore_f,
                    index=index_f
                )
                total += Decimal(str(wscore_f))
            return float(total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))

        activity.total_structure = save_category("structure", structure_domains)
        activity.total_process = save_category("process", process_domains)
        activity.total_outcome = save_category("outcome", outcome_domains)
        activity.status = "done"
        activity.save()

        messages.success(request, "Data has been successfully saved.")
        return redirect('general_surgery_activities')

    return render(request, "accounts/form_gs.html", {
        "activity": activity,
        "structure_domains": structure_domains,
        "process_domains": process_domains,
        "outcome_domains": outcome_domains,
        "detail_dict": detail_dict,
    })


@login_required
def dashboard_gs(request):
    selected_year = int(request.GET.get('year', datetime.now().year))
    selected_period = request.GET.get('period', 'Jan-Jun')

    activities = SurgeryActivity.objects.filter(
        fraternity="General Surgery",
        status="done",
        year=selected_year,
        period=selected_period
    )

    if not activities.exists():
        years = list(range(2020, datetime.now().year + 2))
        context = {
            "selected_year": selected_year,
            "selected_period": selected_period,
            "years": years,
            "total_structure_raw": 0,
            "total_process_raw": 0,
            "total_outcome_raw": 0,
            "total_structure": 0,
            "total_process": 0,
            "total_outcome": 0,
            "overall_index": 0,
            "domain_rows": [],
            "bar_labels": "[]",
            "bar_values": "[]",
        }
        return render(request, "accounts/dashboard_gs.html", context)

    activity = activities.first()
    details = SurgeryActivityDetail.objects.filter(activity=activity)

    total_structure_raw = sum(details.filter(category="structure").values_list("weighted_score", flat=True)) or 0.0
    total_process_raw = sum(details.filter(category="process").values_list("weighted_score", flat=True)) or 0.0
    total_outcome_raw = sum(details.filter(category="outcome").values_list("weighted_score", flat=True)) or 0.0

    total_structure_raw = min(float(total_structure_raw), 1.0)
    total_process_raw = min(float(total_process_raw), 1.0)
    total_outcome_raw = min(float(total_outcome_raw), 1.0)

    total_structure = total_structure_raw * 0.3
    total_process = total_process_raw * 0.4
    total_outcome = total_outcome_raw * 0.3

    overall_index = total_structure + total_process + total_outcome
    overall_index = min(overall_index, 1.0)

    domain_rows = []
    for d in details:
        domain_rows.append({
            "category": d.category.capitalize(),
            "domain": d.domain,
            "performances_value": d.performances_value,
            "target": d.target,
            "weight": d.weight,
            "score": d.score,
            "weighted_score": d.weighted_score,
            "index": d.index,
        })

    years = list(range(2020, datetime.now().year + 2))

    context = {
        "total_structure_raw": round(total_structure_raw, 2),
        "total_process_raw": round(total_process_raw, 2),
        "total_outcome_raw": round(total_outcome_raw, 2),
        "total_structure": round(total_structure, 2),
        "total_process": round(total_process, 2),
        "total_outcome": round(total_outcome, 2),
        "overall_index": round(overall_index, 2),
        "domain_rows": domain_rows,
        "years": years,
        "selected_year": selected_year,
        "selected_period": selected_period,
        "bar_labels": "[]",
        "bar_values": "[]",
    }

    return render(request, "accounts/dashboard_gs.html", context)


# =============================================
# GS COLORECTAL
# =============================================
@login_required
def gscolorectal(request):
    return render(request, "accounts/gscolorectal.html")


@login_required
def gscolorectal_activities(request):
    activities = GSColorectalActivity.objects.annotate(
        period_order=Case(
            When(period='Jan-Jun', then=1),
            When(period='Jul-Dec', then=2),
            default=3,
            output_field=IntegerField()
        )
    ).order_by('year', 'period_order')

    return render(request, 'accounts/gscolorectal_activities.html', {
        'activities': activities
    })


@login_required
def add_gscolorectal_activity(request):
    profile = getattr(request.user, 'profile', None)
    
    if not request.user.is_superuser and (not profile or profile.bidang_pembedahan != 'GS COLORECTAL'):
        messages.error(request, "You do not have permission to add this activity.")
        return redirect('gscolorectal_activities')
    
    current_year = datetime.now().year
    existing = GSColorectalActivity.objects.filter(year=current_year)
    periods_used = [a.period for a in existing]
    
    if len(periods_used) >= 2:
        messages.error(request, "Both periods for this year are already created.")
        return redirect('gscolorectal_activities')
    
    next_period = "Jan-Jun" if "Jan-Jun" not in periods_used else "Jul-Dec"
    
    GSColorectalActivity.objects.create(period=next_period, year=current_year, status='not_started')
    messages.success(request, f"Activity {next_period} {current_year} created successfully!")
    return redirect('gscolorectal_activities')


@login_required
def form_gscolorectal(request, activity_id):
    profile = getattr(request.user, 'profile', None)
    
    if not request.user.is_superuser and (not profile or profile.bidang_pembedahan != 'GS COLORECTAL'):
        messages.error(request, "You do not have permission to access this form.")
        return redirect('gscolorectal_activities')
    
    activity = get_object_or_404(GSColorectalActivity, id=activity_id)
    
    structure_domains = [
        "Number of FTE consultant general surgeons (Ensures adequate expertise for managing complex surgical cases)",
        "Operating rooms equipped for general surgical procedures (including laparoscopic capabilities) (Supports safe surgical practices and reduces intraoperative risks)",
        "Availability of electrocautery units and surgical energy devices (Improves bleeding control during surgery, enhancing safety)",
        "Templates for documenting procedures and post-op care reduce clinical errors (Standardized documentation reduces variability and improves safety)",
        "Clinical guidelines for common surgical conditions (Reduces treatment variation and improves patient safety)",
        "Number of FTE surgeons with sub-specialty interests (Supports safe and focused care for complex conditions)",
        "Availability of complete and functional surgical instrument sets (Prevents errors or delays during procedures due to missing tools)",
        "Surgical morbidity and mortality reviews (Enables continuous learning and improvement from clinical outcomes)",
        "Number of FTE registered nurses dedicated to general surgical care (Ensures safe monitoring and postoperative care)",
        "Availability of stoma care nurses, wound care specialists (Reduces risk of complications through proper wound/stoma management)",
        "Sub-specialty-trained surgeons improve quality of care (Enhances treatment precision and clinical outcomes)",
        "Dedicated clinic and minor procedure rooms (Facilitates timely care for minor cases outside of major theatres)",
        "Laparoscopic towers and instrumentation (Enables minimally invasive surgeries with better outcomes)",
        "Integration of surgical documentation and access to imaging improves decision-making (Supports comprehensive clinical decisions)",
        "Protocols ensure consistent evidence-based practice (Promotes high-quality, standardized care)",
        "Dedicated surgical support staff improve recovery outcomes (Improves postoperative healing through specialized nursing care)",
        "Adequate inpatient surgical ward beds (Supports continuity of care after surgery)",
        "Endoscopy units for diagnostic and therapeutic procedures (Supports accurate, early diagnosis and treatment)",
        "Outcome tracking system enhances quality monitoring (Allows systematic evaluation and improvement of surgical care)",
        "MDT meetings address complex conditions (e.g., colorectal cancer) with tailored care (Ensures care plans are aligned with individual patient needs)",
        "Operating theatre availability and scheduling efficiency (Reduces patient wait times for surgery)",
        "Efficient scheduling and workflow management (Prevents delays and improves overall department performance)",
        "Minor procedure rooms support fast access for outpatient care (Enables quicker interventions for less complex cases)",
        "Ratio of consultant general surgeons to surgical patient volume (Balances workload, prevents bottlenecks, and improves productivity)",
        "Optimized use of operating theatre time (Maximizes surgical throughput without compromising quality)",
        "Advanced surgical tools reduce intraoperative time and complications (Improves workflow and minimizes risk during operations)",
        "Electronic systems streamline documentation, communication, and tracking (Minimizes paperwork, improves coordination)",
        "Allocation of specific beds enhances patient flow (Improves patient admission and discharge efficiency)",
        "Availability of support staff ensures care for specific patient needs (e.g., stoma, wounds) (Ensures all patient groups receive appropriate and targeted support)",
        "Access to surgical consultation rooms and procedures for various patient groups (Ensures inclusivity and service access across all demographics)",
        "Availability of specialized equipment for diverse surgical needs (e.g., GI, laparoscopic) (Ensures all types of patients can be treated appropriately)",
        "Policies ensure access to standardised care for all surgical patients (Prevents disparities in care and ensures fairness)",
        "Integration with imaging and EHR allows cross-departmental care coordination (Enables seamless sharing of information for multidisciplinary care)",
        "Multidisciplinary policies enable collaboration across departments (Supports unified management with other specialties like oncology or radiology)"
    ]
    
    process_domains = [
        "Percentage of patients with completed preoperative assessments (Tracks completion of risk, medical, and surgical readiness assessments before surgery.)",
        "Incidence of wrong-site, wrong-procedure, wrong-patient events (Counts serious preventable surgical errors involving site, procedure, or patient.)",
        "Incidence of major anaesthetic complications in General Surgery patients (Monitors serious events like cardiac arrest or airway failure.)",
        "Incidence of surgical site infections (SSIs) (Tracks the number of infections at the incision site after surgery.)",
        "Percentage of General Surgery patients with documented informed consent (Tracks proper documentation that the patient was informed and agreed.)",
        "Percentage of appropriate referrals to General Surgery (Measures how many referrals meet clinical criteria for General Surgery assessment.)",
        "Percentage of required preoperative investigations completed and reviewed (Checks if all necessary lab and imaging tests are done and reviewed.)",
        "Percentage of General Surgery procedures with completed safety checklists (Measures use of surgical safety checklists before and during surgery.)",
        "Percentage of adherence to anaesthesia safety protocols (Checks how consistently safety practices like equipment checks and dosing are followed.)",
        "Percentage of appropriate sterilization/disinfection of instruments (Monitors correct sterilization procedures for surgical tools.)",
        "Percentage of identified General Surgery problems with documented notes (Measures how well surgical issues are recorded in clinical records.)",
        "Percentage of documented communication with referring providers (Measures if referring doctors are updated with patient care details.)",
        "Patient satisfaction with preoperative information and preparation (Assesses how well patients feel informed and ready for surgery.)",
        "Patient satisfaction with clarity of information from surgery team (Assesses how clearly the surgery plan and risks were explained.)",
        "Time from referral to initial General Surgery consultation (Average time taken from referral receipt to first consultation.)",
        "Timeliness of General Surgery record completion (Tracks how quickly surgical notes and documentation are completed after procedures.)",
        "Percentage of patients screened according to relevant guidelines",
        "Percentage of General Surgery patient records following POMR format (Monitors compliance with standardized perioperative documentation.)",
        "Percentage of intraoperative adverse events (Tracks complications such as bleeding or equipment failure during surgery.)",
        "Percentage of General Surgery patients assessed for anaesthesia risk (Tracks preoperative risk evaluations for anesthesia suitability.)",
        "Percentage of adherence to hand hygiene protocols (Checks how consistently hand hygiene is followed by surgical staff.)"
    ]
    
    outcome_domains = [
        "Hospital-Acquired Infection Rate (Incidence of infections acquired during hospital stay.)",
        "30-Day Mortality Rate (Number of deaths within 30 days post-surgery per 1,000 cases.)",
        "Waiting Time for Elective Surgeries (Average duration from consultation to surgery.)",
        "Reoperation Rate (Percentage of patients requiring additional surgery due to complications.)",
        "Cause-Specific Mortality Analysis (Evaluation of mortality causes to inform quality improvement.)",
        "Complaint Resolution Time (Average time taken to address patient complaints.)",
        "Patient Satisfaction Surveys (Scores reflecting patient experiences and satisfaction.)",
        "Emergency Case Response Time (Time from emergency admission to surgical intervention.)",
        "Average time to address patient complaints (Measures responsiveness of the care system.)",
        "Average duration from consultation to surgery (Total time between first surgical consult and actual surgery as a measure of system efficiency.)",
        "Demographic Analysis of Service Utilization (Assessment of access across different population groups.)",
        "Language and Cultural Support Services (Availability of translation and culturally sensitive care.)",
        "Availability of translation and culturally sensitive care (Measures system integration of diverse patient needs into routine practice.)"
    ]
    
    detail_dict = {}
    all_details = GSColorectalDetail.objects.filter(activity=activity)
    for d in all_details:
        key = f"{d.category}_{d.domain_name}"
        detail_dict[key] = {
            'performances': d.performances_value,
            'target': d.target,
            'weight': d.weight,
            'score': d.score,
            'wscore': d.weighted_score,
            'index': d.index
        }
    
    if request.method == 'POST':
        GSColorectalDetail.objects.filter(activity=activity).delete()
        
        def save_domain(category, domain_name, i):
            performances = request.POST.get(f'{category}_performances_{i}', '0')
            target = request.POST.get(f'{category}_target_{i}', '0')
            weight = request.POST.get(f'{category}_weight_{i}', '0')
            
            score_f, wscore_f, index_f = calculate_domain_scores(performances, target, weight)

            GSColorectalDetail.objects.create(
                activity=activity,
                category=category,
                domain_name=domain_name,
                performances_value=int(performances) if performances else 0,
                target=int(target) if target else 0,
                weight=float(weight) if weight else 0,
                score=score_f,
                weighted_score=wscore_f,
                index=index_f
            )
            
            return Decimal(str(wscore_f))
        
        total_structure = Decimal('0')
        total_process = Decimal('0')
        total_outcome = Decimal('0')
        
        for i, domain in enumerate(structure_domains, start=1):
            total_structure += save_domain('structure', domain, i)
        
        for i, domain in enumerate(process_domains, start=1):
            total_process += save_domain('process', domain, i)
        
        for i, domain in enumerate(outcome_domains, start=1):
            total_outcome += save_domain('outcome', domain, i)
        
        activity.total_structure = total_structure.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        activity.total_process = total_process.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        activity.total_outcome = total_outcome.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        activity.status = 'completed'
        activity.save()
        
        messages.success(request, 'Data saved successfully!')
        return redirect('gscolorectal_activities')
    
    return render(request, "accounts/form_gscolorectal.html", {
        "activity": activity,
        "structure_domains": structure_domains,
        "process_domains": process_domains,
        "outcome_domains": outcome_domains,
        "detail_dict": detail_dict,
    })


@login_required
def dashboard_gscolorectal(request):
    selected_year = int(request.GET.get('year', datetime.now().year))
    selected_period = request.GET.get('period', 'Jan-Jun')
    
    try:
        activity = GSColorectalActivity.objects.get(year=selected_year, period=selected_period)
        total_structure = activity.total_structure
        total_process = activity.total_process
        total_outcome = activity.total_outcome
        overall_index = activity.overall_index
        
        details = GSColorectalDetail.objects.filter(activity=activity)
        domain_rows = []
        for d in details:
            domain_rows.append({
                'category': d.category.capitalize(),
                'domain': d.domain_name,
                'performances_value': d.performances_value,
                'target': d.target,
                'weight': d.weight,
                'score': d.score,
                'weighted_score': d.weighted_score,
                'index': d.index
            })
    except GSColorectalActivity.DoesNotExist:
        total_structure = 0
        total_process = 0
        total_outcome = 0
        overall_index = 0
        domain_rows = []
    
    years = GSColorectalActivity.objects.values_list('year', flat=True).distinct().order_by('-year')
    if not years:
        years = [datetime.now().year]
    
    return render(request, 'accounts/dashboard_gscolorectal.html', {
        'total_structure': total_structure,
        'total_process': total_process,
        'total_outcome': total_outcome,
        'overall_index': overall_index,
        'domain_rows': domain_rows,
        'years': years,
        'selected_year': selected_year,
        'selected_period': selected_period,
        'bar_labels': '[]',
        'bar_values': '[]'
    })


# =============================================
# OPHTHALMOLOGY
# =============================================
@login_required
def ophthalmology(request):
    return render(request, 'accounts/ophthalmology.html')


@login_required
def ophthalmology_activities(request):
    year = datetime.now().year
    
    activities = SurgeryActivity.objects.filter(
        fraternity="Ophthalmology",
        year=year
    ).annotate(
        period_order=Case(
            When(period='Jan-Jun', then=1),
            When(period='Jul-Dec', then=2),
            default=3,
            output_field=IntegerField()
        )
    ).order_by('period_order')

    return render(request, "accounts/ophthalmology_activities.html", {
        "activities": activities,
        "year": year,
    })


@login_required
def add_ophthalmology_activity(request):
    profile = getattr(request.user, 'profile', None)
    
    # ✅ STRICT CHECK (superadmin bypasses)
    if not request.user.is_superuser and (not profile or profile.bidang_pembedahan != 'OPHTHALMOLOGY'):
        messages.error(request, "You do not have permission to add this activity.")
        return redirect("ophthalmology_activities")
    
    year = datetime.now().year
    existing = SurgeryActivity.objects.filter(
        fraternity="Ophthalmology",
        year=year
    ).count()

    if existing == 0:
        period = "Jan-Jun"
    elif existing == 1:
        period = "Jul-Dec"
    else:
        messages.error(request, "The activities for this year are already complete.")
        return redirect("ophthalmology_activities")

    activity, created = SurgeryActivity.objects.get_or_create(
        fraternity="Ophthalmology",
        year=year,
        period=period
    )
    activity.users.add(request.user)
    messages.success(request, f"You have been added to the activity {period} {year}.")
    return redirect("ophthalmology_activities")


@login_required
def form_ophthalmology(request, activity_id):
    profile = getattr(request.user, 'profile', None)
    
    # ✅ STRICT CHECK (superadmin bypasses)
    if not request.user.is_superuser and (not profile or profile.bidang_pembedahan != 'OPHTHALMOLOGY'):
        messages.error(request, "You do not have permission to access this form.")
        return redirect('ophthalmology_activities')
    
    activity = get_object_or_404(SurgeryActivity, id=activity_id)

    structure_domains = [
        "KOSPEN cataract finder policy (Written policy ensuring all KOSPEN group members are trained as cataract finders, per National Sensory Health Policy)",
        "Vision screening for patients above 60 years at KK (All patients above 60 years old attending KK to be checked for visual impairment)",
        "Referral of low vision patients to primary care optometrist (All patients above 60 with vision worse than 6/12 to be referred to primary care optometrist)",
        "MOH Cataract Management Pathway guideline (Established guideline based on WHO for all hospitals with Ophthalmology Services)",
        "Refraction room for optometrist at Level 1 KK (All Level 1 KK to have dedicated refraction room for optometrist)",
        "Dedicated ultraclean ophthalmology operating theatre (All hospitals with ophthalmologist to have daycare surgery facilities per infection control policy)",
        "Klinik Katarak KKM mobile set availability (Available in East Coast, Sabah and Sarawak to extend cataract surgical access)",
        "RALoV Flip Chart availability (Rapid Assessment for Low Vision chart for adults, distributed per clinic)",
        "Smart vision chart per clinic (At least 1 smart vision chart or RALoV Flip Chart available at every clinic)",
        "Slit lamp per clinic (At least 1 slit lamp available at every clinic for anterior segment examination)",
        "Refraction set and optometrist examination chair per clinic (At least 1 set per clinic to support routine eye examination)",
        "Fully equipped hospital facilities for optometrist (Hospital with Optometrist but no ophthalmologist to meet minimum facility standards)",
        "Hospital with ophthalmologist or permanent cataract outreach (Facilities supporting outreach cataract surgery at designated KKM centres)",
        "KOSPEN centres with trained cataract finders and RALoV Chart (All community centres with KOSPEN to have at least 2 trained cataract finders)",
        "Level 1 KK with optometrist per state (Every state to have at least 2 Level 1 KK with optometrist, except Perlis)",
        "Minimum optometrist staffing for ophthalmology clinics (5 optometrists for non-state hospitals, 10 for state hospitals, based on WISN norm)",
        "Budget for Annual Primary Eye Care Training (Funding allocated for FMS training every cycle of C&P, for every state)",
        "National ToT for phaco trainers (National Training of Trainers programme for phacoemulsification surgical training)",
        "MySejahtera vision screening question (MySejahtera platform to include at least one question on patient vision status)",
        "Patient journey mapping for cataract (Documented cataract patient pathway from screening to surgical outcome)"
    ]
    
    process_domains = [
        "Cataract patients referred to KK and seen (Number of patients with cataract referred to Klinik Kesihatan and attended their appointment)",
        "Cataract patients referred to eye clinic and seen (Number of patients referred to eye clinic and successfully seen at KKKKM)",
        "Cataract surgery waiting time (Target of less than 6 months from referral to surgery)",
        "Cancellation rate of elective cataract surgery (Proportion of scheduled elective cataract surgeries that were cancelled)",
        "SSSL practice audit (Audit of Safe Surgery Save Lives practice compliance at ophthalmology units)",
        "POMR Reporting (Compliance with Patient Outcome and Mortality Review reporting at ophthalmology units)",
        "PCI practice audit compliance (Prevention and Control of Infection audit, minimum once per year per centre)"
    ]
    
    outcome_domains = [
        "Cataract surgery performed under Daycare (Proportion of cataract surgeries completed as daycare without hospital admission)",
        "Cataract complication rate (Rate of intraoperative and postoperative complications following cataract surgery)",
        "Post-operative refractive surprise rate (Audit of cases within +/- 1 Diopter from targeted refraction, at least once per year)",
        "Audit completion rate (Target of 1 audit per year per centre, with a benchmark of 50 cases per centre)",
        "Rate of elective post-operative endophthalmitis (Sentinel event rate of infection following elective cataract surgery)",
        "Anaesthesia-related mortality rate (Percentage of anaesthesia-related deaths among ophthalmology surgical patients)",
        "Infectious endophthalmitis following cataract surgery (Target of no more than 2 cases per 1,000 cataract operations)",
        "BCVA better than 6/12 within 3 months post-surgery (Proportion of patients with no co-morbidity achieving 6/12 or better vision)",
        "Visual acuity outcome in patients without co-morbidity (Percentage achieving 6/12 or better within 3 months of cataract surgery)",
        "IOL availability rate (Rate of patients requiring out-of-pocket payment for IOL due to unavailability of subsidised options)",
        "IOL availability for all cataract surgery patients (All patients needing IOL to have access via out-of-pocket, subsidy or sponsorship)",
        "Pathway to acquire IOL for Malaysian citizens (Defined and accessible pathway for ageing population to obtain IOL)"
    ]

    details = SurgeryActivityDetail.objects.filter(activity=activity)
    detail_dict = {}
    for d in details:
        key = f"{d.category}_{d.domain}"
        detail_dict[key] = {
            "performances": d.performances_value,
            "target": d.target,
            "weight": d.weight,
            "score": d.score,
            "wscore": d.weighted_score,
            "index": d.index
        }

    if request.method == "POST":
        SurgeryActivityDetail.objects.filter(activity=activity).delete()

        def save_category(category_name, domains):
            total = Decimal('0')
            for i, domain in enumerate(domains, start=1):
                performances = request.POST.get(f"{category_name}_performances_{i}", "0")
                target = request.POST.get(f"{category_name}_target_{i}", "0")
                weight = request.POST.get(f"{category_name}_weight_{i}", "0")

                score_f, wscore_f, index_f = calculate_domain_scores(performances, target, weight)

                SurgeryActivityDetail.objects.create(
                    activity=activity,
                    category=category_name,
                    domain=domain,
                    performances_value=int(performances) if performances else 0,
                    target=int(target) if target else 0,
                    weight=float(weight) if weight else 0,
                    score=score_f,
                    weighted_score=wscore_f,
                    index=index_f
                )
                total += Decimal(str(wscore_f))
            return float(total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))

        activity.total_structure = save_category("structure", structure_domains)
        activity.total_process = save_category("process", process_domains)
        activity.total_outcome = save_category("outcome", outcome_domains)
        activity.status = "done"
        activity.save()

        messages.success(request, "Data has been successfully saved.")
        return redirect('ophthalmology_activities')

    return render(request, "accounts/form_ophthalmology.html", {
        "activity": activity,
        "structure_domains": structure_domains,
        "process_domains": process_domains,
        "outcome_domains": outcome_domains,
        "detail_dict": detail_dict,
    })


@login_required
def dashboard_ophthalmology(request):
    selected_year = int(request.GET.get('year', datetime.now().year))
    selected_period = request.GET.get('period', 'Jan-Jun')

    activities = SurgeryActivity.objects.filter(
        fraternity="Ophthalmology",
        status="done",
        year=selected_year,
        period=selected_period
    )

    if not activities.exists():
        context = {
            "selected_year": selected_year,
            "selected_period": selected_period,
            "years": list(range(2020, datetime.now().year + 2)),
            "total_structure_raw": 0,
            "total_process_raw": 0,
            "total_outcome_raw": 0,
            "total_structure": 0,
            "total_process": 0,
            "total_outcome": 0,
            "overall_index": 0,
            "domain_rows": []
        }
        return render(request, "accounts/dashboard_ophthalmology.html", context)

    activity = activities.first()
    details = SurgeryActivityDetail.objects.filter(activity=activity)

    total_structure_raw = sum(details.filter(category="structure").values_list("weighted_score", flat=True)) or 0.0
    total_process_raw = sum(details.filter(category="process").values_list("weighted_score", flat=True)) or 0.0
    total_outcome_raw = sum(details.filter(category="outcome").values_list("weighted_score", flat=True)) or 0.0

    total_structure_raw = min(float(total_structure_raw), 1.0)
    total_process_raw = min(float(total_process_raw), 1.0)
    total_outcome_raw = min(float(total_outcome_raw), 1.0)

    total_structure = total_structure_raw * 0.5
    total_process = total_process_raw * 0.3
    total_outcome = total_outcome_raw * 0.2

    overall_index = total_structure + total_process + total_outcome
    overall_index = min(overall_index, 1.0)

    domain_rows = []
    for d in details:
        domain_rows.append({
            "category": d.category.capitalize(),
            "domain": d.domain,
            "performances_value": d.performances_value,
            "target": d.target,
            "weight": d.weight,
            "score": d.score,
            "weighted_score": d.weighted_score,
            "index": d.index,
        })

    context = {
        "selected_year": selected_year,
        "selected_period": selected_period,
        "years": list(range(2020, datetime.now().year + 2)),
        "total_structure_raw": round(total_structure_raw, 2),
        "total_process_raw": round(total_process_raw, 2),
        "total_outcome_raw": round(total_outcome_raw, 2),
        "total_structure": round(total_structure, 2),
        "total_process": round(total_process, 2),
        "total_outcome": round(total_outcome, 2),
        "overall_index": round(overall_index, 2),
        "domain_rows": domain_rows,
    }

    return render(request, "accounts/dashboard_ophthalmology.html", context)


# =============================================
# EMERGENCY & TRAUMA
# =============================================
@login_required
def emergency_trauma(request):
    return render(request, 'accounts/emergency_trauma.html')


@login_required
def emergency_trauma_activities(request):
    activities = EmergencyTraumaActivity.objects.annotate(
        period_order=Case(
            When(period='Jan-Jun', then=1),
            When(period='Jul-Dec', then=2),
            default=3,
            output_field=IntegerField()
        )
    ).order_by('year', 'period_order')

    return render(request, 'accounts/emergency_trauma_activities.html', {
        'activities': activities
    })


@login_required
def add_emergency_trauma_activity(request):
    profile = getattr(request.user, 'profile', None)
    
    if not request.user.is_superuser and (not profile or profile.bidang_pembedahan != 'EMERGENCY & TRAUMA'):
        messages.error(request, "You do not have permission to add this activity.")
        return redirect('emergency_trauma_activities')
    
    current_year = datetime.now().year
    existing = EmergencyTraumaActivity.objects.filter(year=current_year)
    periods_used = [a.period for a in existing]
    
    if len(periods_used) >= 2:
        messages.error(request, "Both periods for this year are already created.")
        return redirect('emergency_trauma_activities')
    
    next_period = "Jan-Jun" if "Jan-Jun" not in periods_used else "Jul-Dec"
    
    EmergencyTraumaActivity.objects.create(period=next_period, year=current_year, status='not_started')
    messages.success(request, f"Activity {next_period} {current_year} created successfully!")
    return redirect('emergency_trauma_activities')


@login_required
def form_emergency_trauma(request, activity_id):
    profile = getattr(request.user, 'profile', None)
    
    if not request.user.is_superuser and (not profile or profile.bidang_pembedahan != 'EMERGENCY & TRAUMA'):
        messages.error(request, "You do not have permission to access this form.")
        return redirect('emergency_trauma_activities')
    
    activity = get_object_or_404(EmergencyTraumaActivity, id=activity_id)
    
    structure_domains = [
        "Number of FTE consultant emergency physicians (Ensures adequate expertise in managing acute emergencies)",
        "Number of resuscitation bays (Enables safe stabilization of critical patients)",
        "Availability of defibrillators, ventilators, airway equipment (Essential to life-saving interventions)",
        "Real-time visibility of patient location and status in EDIS (Prevents loss or delay of care through tracking)",
        "Existence of triage protocols (Ensures systematic and safe patient prioritization)",
        "Number of FTE physicians with sub-specialty training within emergency medicine (Improves safety in handling complex, high-risk cases)",
        "Availability of isolation rooms (Prevents spread of infectious diseases)",
        "Adequate supply of emergency medications (Prevents delay in time-critical drug administration)",
        "Accurate and updated clinical records (Improves safety through reliable documentation)",
        "Policies on escalation of care (Defines clear action steps for clinical deterioration)",
        "Number of FTE registered nurses specifically trained in emergency care (Supports high-standard emergency nursing care)",
        "Dedicated areas for paediatric emergencies (Provides safe, age-appropriate emergency care)",
        "Mechanisms for mortality reviews and critical incident reporting (Supports learning and prevention of future errors)",
        "Availability of triage nurses (Ensures safe and timely categorization of patient acuity)",
        "Availability of paramedics or EMTs (Enhances pre-hospital safety and seamless patient transfer)",
        "Number of FTE physicians with sub-specialty training (paediatric EM, toxicology, critical care) (Supports evidence-based care across subdomains of emergency medicine)",
        "Number of acute care beds/cubicles (Improves capacity to manage high patient load effectively)",
        "Availability of ultrasound machines (Improves diagnostic precision in trauma and critical care)",
        "Electronic documentation and order entry within the ED (Reduces errors and streamlines clinical processes)",
        "Clinical guidelines for common presentations (Standardizes management and improves outcomes)",
        "Skilled nursing and paramedic support improves care outcomes (Multidisciplinary expertise enhances quality and precision of care)",
        "Designated fast-track or minor injuries areas (Streamlines care delivery for less severe cases)",
        "Access to point-of-care testing devices (POCT) (Enables immediate lab results for quicker decision-making)",
        "Seamless access to full patient history (Enhances clinical judgment with comprehensive data)",
        "Adherence to emergency care standards (Maintains quality and consistency of care)",
        "Dedicated areas for paediatric emergencies (Reduces stress and enhances comfort for children and families)",
        "Protocols structured around needs of emergency patients (Ensures care is responsive, appropriate, and respectful)",
        "Minor injury and fast-track zones enhance patient comfort and reduce wait (Improves experience for low-acuity patients)",
        "Designated fast-track/minor injury areas streamline low-acuity care (Speeds up treatment and prevents ED crowding)",
        "Immediate access to radiology services (e.g., on-site X-ray) (Speeds up diagnosis and treatment initiation)",
        "Real-time EDIS improves decision-making and communication (Speeds up coordination among staff and departments)",
        "Efficient patient flow pathways (Minimizes wait times and delays in care transitions)",
        "Point-of-care testing improves rapid diagnosis (Reduces lab wait time in urgent situations)",
        "Ratio of consultant emergency physicians to patient volume (Ensures workload is balanced, reducing delays and burnout)",
        "Proximity to radiology and laboratory (Reduces turnaround time for diagnostics)",
        "Well-stocked and functional resuscitation and diagnostic equipment supports throughput (Prevents workflow disruption and supports high-volume care)",
        "Integration with hospital EHR enables electronic referrals and investigations (Reduces duplication and speeds up clinical workflows)",
        "Optimized space layout for patient movement (Improves workflow efficiency and care delivery)",
        "Sufficiently trained multidisciplinary workforce to meet varied patient needs (adults, children, trauma, etc.) (Promotes accessible and appropriate care across all demographics and conditions)",
        "Facilities designed for all patient groups, including paediatrics and infectious cases (Ensures no group is underserved or overlooked)",
        "Policies ensure fair and appropriate care access regardless of urgency or complexity (Supports non-discriminatory and inclusive service delivery)",
        "Full integration of EDIS with hospital-wide systems (Supports coordinated care beyond the ED)",
        "Governance aligned with hospital-wide safety and quality oversight (Promotes seamless operations across departments and services)"
    ]
    
    process_domains = [
        "Percentage of time-critical activations ≤ target (Share of stroke, STEMI, and trauma activations meeting published door-to-CT, door-to-balloon, or door-to-OR benchmarks.)",
        "Airway evaluation completeness (Proportion of high-risk patients with documented airway assessment before procedural sedation or intubation.)",
        "Procedural-time-out compliance (Proportion of invasive ED procedures—like central line or chest tube insertions—with a documented pre-procedure time-out.)",
        "Sedation-monitoring adherence (Proportion of ED sedation cases with continuous capnography, pulse oximetry, and blood pressure monitoring per protocol.)",
        "Hand-hygiene compliance (Proportion of observed hand-hygiene opportunities completed before and after patient contact.)",
        "ED POMR review rate (Proportion of deaths in the ED or within 24 hours of ED departure reviewed in a multidisciplinary mortality meeting.)",
        "High-risk consent completeness (Proportion of patients undergoing high-risk ED procedures—e.g., thrombolysis, intubation—with documented informed consent.)",
        "Isolation-precautions adherence (Proportion of patients with suspected airborne/contact infections placed on proper isolation within 30 minutes of triage.)",
        "Resuscitation bundle activation rate (Proportion of septic or hemorrhagic shock patients managed per bundle—fluids, antibiotics, blood—within 1 hour.)",
        "Family-update compliance (Proportion of critical-care boarders with documented family communication at least once per shift.)",
        "Door-to-triage time ≤ 10 min (Proportion of all arrivals assigned a triage level within ten minutes of ED registration.)",
        "Family-update compliance per shift (Focuses on ensuring family updates happen regularly, ideally every shift.)"
    ]
    
    outcome_domains = [
        "Procedure-related complication rate: Proportion of ED procedures (e.g. central line, chest tube) resulting in a major adverse event (e.g. pneumothorax, bleeding).",
        "ED-related POMR: Proportion of deaths occurring in the ED or within same-admission post-ED procedures among all ED arrivals.",
        "Compliance rate with infection prevention protocols in emergency surgery: (Adherence to aseptic and infection-prevention standards in emergency surgery.)",
        "Average time from ED admission to transfer or discharge (Mean duration from emergency department arrival to hospital admission, transfer, or discharge.)",
        "Percentage of emergency surgeries initiated with complete surgical safety checklists: (Proportion of emergency surgeries that followed full safety checklist protocols.)",
        "POMR for emergency surgical cases (Mortality rate among patients undergoing emergency surgery, regardless of procedure type.)",
        "Percentage of patients reporting effective communication during emergency care: (Proportion of patients who felt their concerns were clearly understood by providers.)",
        "Gender and age equity in emergency outcomes (Comparison of ED outcomes across gender and age groups to ensure fairness.)",
        "Number of patients leaving without being seen (Count of patients who registered but left the ED before being assessed by a clinician.)",
        "ED patient-experience score: Average satisfaction rating (0–100) from post-visit surveys covering wait times, communication and environment.",
        "Availability of interpretation services (Presence of multilingual and interpreter services to support diverse patients in the ED.)",
        "Patient satisfaction score for emergency department experience: Overall satisfaction score based on ED experience.)",
        "Average time from arrival to first clinical assessment (Mean time from patient arrival at ED to first evaluation by medical personnel.)",
        "Percentage of emergency surgeries delayed due to safety or resource constraints: (Proportion of emergency surgeries postponed because of equipment, staffing, or patient safety concerns.)",
        "Waiting time as perceived and reported by patients; (Waiting time as understood and reported by patients themselves.)",
        "Geographic access equity (arrival-to-treatment gaps urban vs rural): Difference in median arrival-to-treatment intervals between patients from urban vs rural catchment areas.",
        "Door-to-doctor time ≤ 15 min: Proportion of patients first assessed by an emergency physician within 15 minutes of triage.",
        "Emergency department bed occupancy rate: (Percentage of available emergency beds occupied at any given time.)",
        "Rate of unplanned returns to surgery from emergency department interventions: (Frequency of repeat emergency surgeries required due to prior intervention failure.)",
        "Mortality by urgency and case complexity (Death rate analyzed by how urgent the surgery was and the complexity of the condition.)",
        "Complaint rate related to emergency care (Number of patient complaints regarding emergency medical treatment or service.)",
        "Disparities in outcomes by ethnicity/vulnerability (Difference in care quality or outcomes for ethnic or socioeconomically vulnerable populations.)",
        "ED-to-ICU transfer time ≤ 60 min: Proportion of ED patients requiring ICU care physically transferred from ED to ICU within one hour of decision.",
        "Time to care regardless of socioeconomic or demographic status (Assessment of whether treatment access times are consistent across all population groups.)",
        "Patient confidence in staff and services (Proportion of patients expressing trust in emergency care regardless of background.)",
        "Triage-level equity (Consistency in triage scoring regardless of social status.)",
        "Percentage of cases served from underserved/rural areas (Proportion of total ED visits from marginalized or rural populations.)",
        "Percentage triaged within target timeframes by severity (Proportion of patients seen within benchmarked triage times based on acuity level.)",
        "Rate of adverse events during emergency surgical procedures: (Incidence of complications like bleeding, organ injury, or anesthesia issues during emergency surgery.)",
        "Number of deaths within thirty days following emergency surgical intervention: (Number of deaths occurring within 30 days after an emergency surgical intervention.)"
    ]
    
    detail_dict = {}
    all_details = EmergencyTraumaDetail.objects.filter(activity=activity)
    for d in all_details:
        key = f"{d.category}_{d.domain_name}"
        detail_dict[key] = {
            'performances': d.performances_value,
            'target': d.target,
            'weight': d.weight,
            'score': d.score,
            'wscore': d.weighted_score,
            'index': d.index,
        }
    
    if request.method == 'POST':
        EmergencyTraumaDetail.objects.filter(activity=activity).delete()
        
        def save_domain(category, domain_name, i):
            performances = request.POST.get(f'{category}_performances_{i}', '0')
            target = request.POST.get(f'{category}_target_{i}', '0')
            weight = request.POST.get(f'{category}_weight_{i}', '0')
            
            score_f, wscore_f, index_f = calculate_domain_scores(performances, target, weight)
            
            EmergencyTraumaDetail.objects.create(
                activity=activity,
                category=category,
                domain_name=domain_name,
                performances_value=int(performances) if performances else 0,
                target=int(target) if target else 0,
                weight=float(weight) if weight else 0,
                score=score_f,
                weighted_score=wscore_f,
                index=index_f
            )
            
            return Decimal(str(wscore_f))
        
        total_structure = Decimal('0')
        for i, domain in enumerate(structure_domains, start=1):
            total_structure += save_domain("structure", domain, i)
        
        total_process = Decimal('0')
        for i, domain in enumerate(process_domains, start=1):
            total_process += save_domain("process", domain, i)
        
        total_outcome = Decimal('0')
        for i, domain in enumerate(outcome_domains, start=1):
            total_outcome += save_domain("outcome", domain, i)
        
        activity.total_structure = float(total_structure)
        activity.total_process = float(total_process)
        activity.total_outcome = float(total_outcome)
        activity.status = 'done'
        activity.save()
        
        messages.success(request, "Emergency & Trauma data saved successfully!")
        return redirect('emergency_trauma_activities')
    
    context = {
        'activity': activity,
        'structure_domains': structure_domains,
        'process_domains': process_domains,
        'outcome_domains': outcome_domains,
        'detail_dict': detail_dict,
    }
    return render(request, 'accounts/form_emergency_trauma.html', context)


@login_required
def dashboard_emergency_trauma(request):
    selected_year = int(request.GET.get('year', datetime.now().year))
    selected_period = request.GET.get('period', 'Jan-Jun')

    activities = EmergencyTraumaActivity.objects.filter(
        status="done",
        year=selected_year,
        period=selected_period
    )

    if not activities.exists():
        context = {
            'selected_year': selected_year,
            'selected_period': selected_period,
            'years': list(range(2020, datetime.now().year + 2)),
            'total_structure_raw': 0,
            'total_process_raw': 0,
            'total_outcome_raw': 0,
            'total_structure': 0,
            'total_process': 0,
            'total_outcome': 0,
            'overall_saoi': 0,
            'domain_rows': []
        }
        return render(request, 'accounts/dashboard_emergency_trauma.html', context)

    activity = activities.first()
    details = EmergencyTraumaDetail.objects.filter(activity=activity)

    total_structure_raw = sum(d.weighted_score for d in details.filter(category="structure"))
    total_process_raw = sum(d.weighted_score for d in details.filter(category="process"))
    total_outcome_raw = sum(d.weighted_score for d in details.filter(category="outcome"))

    total_structure_raw = min(float(total_structure_raw), 1.0)
    total_process_raw = min(float(total_process_raw), 1.0)
    total_outcome_raw = min(float(total_outcome_raw), 1.0)

    total_structure = total_structure_raw * 0.5
    total_process = total_process_raw * 0.3
    total_outcome = total_outcome_raw * 0.2

    overall_saoi = total_structure + total_process + total_outcome
    overall_saoi = min(overall_saoi, 1.0)

    domain_rows = []
    for d in details:
        domain_rows.append({
            'category': d.category.capitalize(),
            'domain': d.domain_name,
            'performances_value': d.performances_value,
            'target': d.target,
            'weight': d.weight,
            'score': d.score,
            'weighted_score': d.weighted_score,
            'index': d.index,
        })

    return render(request, 'accounts/dashboard_emergency_trauma.html', {
        'total_structure_raw': round(total_structure_raw, 2),
        'total_process_raw': round(total_process_raw, 2),
        'total_outcome_raw': round(total_outcome_raw, 2),
        'total_structure': round(total_structure, 2),
        'total_process': round(total_process, 2),
        'total_outcome': round(total_outcome, 2),
        'overall_saoi': round(overall_saoi, 2),
        'domain_rows': domain_rows,
        'years': list(range(2020, datetime.now().year + 2)),
        'selected_year': selected_year,
        'selected_period': selected_period,
    })


# =============================================
# ANAESTHESIA
# =============================================
@login_required
def anaesthesia(request):
    return render(request, 'accounts/anaesthesia.html')

@login_required
def anaesthesia_activities(request):
    activities = AnaesthesiaActivity.objects.annotate(
        period_order=Case(
            When(period='Jan-Jun', then=1),
            When(period='Jul-Dec', then=2),
            default=3,
            output_field=IntegerField()
        )
    ).order_by('year', 'period_order')
    return render(request, 'accounts/anaesthesia_activities.html', {'activities': activities})

@login_required
def add_anaesthesia_activity(request):
    profile = getattr(request.user, 'profile', None)
    if not request.user.is_superuser and (not profile or profile.bidang_pembedahan != 'ANAESTHESIA'):
        messages.error(request, "You do not have permission to add this activity.")
        return redirect('anaesthesia_activities')
    
    current_year = datetime.now().year
    existing = AnaesthesiaActivity.objects.filter(year=current_year)
    periods_used = [a.period for a in existing]
    
    if len(periods_used) >= 2:
        messages.error(request, "Both periods for this year are already created.")
        return redirect('anaesthesia_activities')
    
    next_period = "Jan-Jun" if "Jan-Jun" not in periods_used else "Jul-Dec"
    AnaesthesiaActivity.objects.create(period=next_period, year=current_year, status='not_started')
    messages.success(request, f"Activity {next_period} {current_year} created successfully!")
    return redirect('anaesthesia_activities')

@login_required
def delete_anaesthesia_activity(request, activity_id):
    profile = getattr(request.user, 'profile', None)
    if not request.user.is_superuser and (not profile or profile.bidang_pembedahan != 'ANAESTHESIA'):
        messages.error(request, "You do not have permission to delete this activity.")
        return redirect('anaesthesia_activities')

    activity = get_object_or_404(AnaesthesiaActivity, id=activity_id)
    activity.delete()
    messages.success(request, "Activity has been successfully deleted/reset.")
    return redirect('anaesthesia_activities')

@login_required
def form_anaesthesia(request, activity_id):
    profile = getattr(request.user, 'profile', None)
    if not request.user.is_superuser and (not profile or profile.bidang_pembedahan != 'ANAESTHESIA'):
        messages.error(request, "You do not have permission to access this form.")
        return redirect('anaesthesia_activities')
    
    activity = get_object_or_404(AnaesthesiaActivity, id=activity_id)
    
    structure_domains = [
        "National Anaesthesia and Critical Care Policy",
        "Specialist hospital with anaesthesiologist have fully equipped: i. anaesthetic clinic ii. operating theatres iii. recovery areas iv. ICU level 3",
        "Train FMS on standard investigation for surgery",
        "Benchmarking norm creation for Anaesthesiologist",
        "Funding as per activity code",
        "Infographic regarding safe anaesthesia",
        "Electronic health records (GA forms, POMR registry, audit database) and paper-based record"
    ]
    
    process_domains = [
        "Establishment of Multidiscipline pre-op assessment and risk stratification for uncertainty risk against benefit of operation",
        "Percentage of elective list cancelled by Anaesthetist after seen at anaesthetic clinic",
        "Every specialist based hospital takes anaesthetic consent for all elective cases seen at the anaesthetic clinic",
        "Full adherence to Safe Surgery Saves Lives (SSSL) checklist",
        "Adherence to MSA minimal monitoring standard, difficult airway algorithm",
        "Percentage of Submission POMR reporting through MPIS",
        "Adherence to Guideline on Infection control in Anaethesia - guideline to HOD and ensure echo training"
    ]
    
    outcome_domains = [
        "Hosp with APS Unit certified with PFH.",
        "Retained anaesthesia foreign body (sentinel event)",
        "Anaesthesia related mortality",
        "Patient satisfaction by APS (Good & Excellent)",
        "Equal anaesthesia access to all patients"
    ]
    
    detail_dict = {}
    all_details = AnaesthesiaDetail.objects.filter(activity=activity)
    for d in all_details:
        key = f"{d.category}_{d.domain_name}"
        detail_dict[key] = {
            'performances': d.performances_value,
            'denominator': d.denominator,
            'target': d.target,
            'weight': d.weight,
            'score': d.score,
            'wscore': d.weighted_score,
            'index': d.index
        }
    
    if request.method == 'POST':
        AnaesthesiaDetail.objects.filter(activity=activity).delete()
        
        def save_domain(category, domain_name, i):
            performances = request.POST.get(f'{category}_performances_{i}', '0')
            denominator = request.POST.get(f'{category}_denominator_{i}', '0')
            target = request.POST.get(f'{category}_target_{i}', '0')
            weight = request.POST.get(f'{category}_weight_{i}', '0')
            
            try: num_d = Decimal(str(performances))
            except: num_d = Decimal('0')
            
            try: den_d = Decimal(str(denominator))
            except: den_d = Decimal('0')
            
            try: wgt_d = Decimal(str(weight))
            except: wgt_d = Decimal('0')
            
            if den_d > 0:
                score_d = (num_d / den_d) * Decimal('100')
                wscore_d = (num_d / den_d) * wgt_d
                index_d = num_d / den_d
            else:
                score_d = Decimal('0')
                wscore_d = Decimal('0')
                index_d = Decimal('0')
                
            score_f = float(score_d.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
            wscore_f = float(wscore_d.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
            index_f = float(index_d.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
            
            AnaesthesiaDetail.objects.create(
                activity=activity, 
                category=category, 
                domain_name=domain_name,
                performances_value=int(performances) if performances else 0,
                denominator=int(denominator) if denominator else 0,
                target=int(target) if target else 0,
                weight=float(weight) if weight else 0,
                score=score_f, 
                weighted_score=wscore_f, 
                index=index_f
            )
            return Decimal(str(wscore_f))
        
        total_structure = Decimal('0')
        for i, domain in enumerate(structure_domains, start=1): 
            total_structure += save_domain('structure', domain, i)
        
        total_process = Decimal('0')
        for i, domain in enumerate(process_domains, start=1): 
            total_process += save_domain('process', domain, i)
        
        total_outcome = Decimal('0')
        for i, domain in enumerate(outcome_domains, start=1): 
            total_outcome += save_domain('outcome', domain, i)
        
        activity.total_structure = float(total_structure.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
        activity.total_process = float(total_process.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
        activity.total_outcome = float(total_outcome.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
        activity.status = 'completed'
        activity.save()
        
        messages.success(request, 'Data saved successfully!')
        return redirect('anaesthesia_activities')
    
    return render(request, "accounts/form_anaesthesia.html", {
        "activity": activity,
        "structure_domains": structure_domains,
        "process_domains": process_domains,
        "outcome_domains": outcome_domains,
        "detail_dict": detail_dict,
    })

@login_required
def dashboard_anaesthesia(request):
    selected_year = int(request.GET.get('year', datetime.now().year))
    selected_period = request.GET.get('period', 'Jan-Jun')
    
    activities = AnaesthesiaActivity.objects.filter(
        status="completed",
        year=selected_year,
        period=selected_period
    )
    
    if not activities.exists():
        context = {
            "selected_year": selected_year, "selected_period": selected_period,
            "years": list(range(2020, datetime.now().year + 2)),
            "total_structure_raw": 0, "total_process_raw": 0, "total_outcome_raw": 0,
            "total_structure": 0, "total_process": 0, "total_outcome": 0,
            "overall_index": 0, "domain_rows": [],
        }
        return render(request, "accounts/dashboard_anaesthesia.html", context)

    activity = activities.first()
    details = AnaesthesiaDetail.objects.filter(activity=activity)

    total_structure_raw = min(float(sum(details.filter(category="structure").values_list("weighted_score", flat=True)) or 0.0), 1.0)
    total_process_raw   = min(float(sum(details.filter(category="process").values_list("weighted_score", flat=True)) or 0.0), 1.0)
    total_outcome_raw   = min(float(sum(details.filter(category="outcome").values_list("weighted_score", flat=True)) or 0.0), 1.0)

    # Pemberat Excel Anaesthesia: 0.3, 0.4, 0.3
    total_structure = total_structure_raw * 0.3
    total_process   = total_process_raw   * 0.4
    total_outcome   = total_outcome_raw   * 0.3
    overall_index   = min(total_structure + total_process + total_outcome, 1.0)

    domain_rows = [{
        "category": d.category.capitalize(),
        "domain": d.domain_name,
        "performances_value": d.performances_value,
        "target": d.target,
        "weight": d.weight,
        "score": d.score,
        "weighted_score": d.weighted_score,
        "index": d.index,
    } for d in details]

    context = {
        "total_structure_raw": round(total_structure_raw, 2), "total_process_raw": round(total_process_raw, 2), "total_outcome_raw": round(total_outcome_raw, 2),
        "total_structure": round(total_structure, 2), "total_process": round(total_process, 2), "total_outcome": round(total_outcome, 2),
        "overall_index": round(overall_index, 2), "domain_rows": domain_rows,
        "years": list(range(2020, datetime.now().year + 2)),
        "selected_year": selected_year, "selected_period": selected_period,
    }
    return render(request, "accounts/dashboard_anaesthesia.html", context)


# =============================================
# UPPER GI
# =============================================
@login_required
def upper_gi(request):
    return render(request, 'accounts/upper_gi.html')


@login_required
def upper_gi_activities(request):
    activities = UpperGIActivity.objects.annotate(
        period_order=Case(
            When(period='Jan-Jun', then=1),
            When(period='Jul-Dec', then=2),
            default=3,
            output_field=IntegerField()
        )
    ).order_by('year', 'period_order')

    return render(request, 'accounts/upper_gi_activities.html', {
        'activities': activities
    })


@login_required
def add_upper_gi_activity(request):
    profile = getattr(request.user, 'profile', None)
    
    if not request.user.is_superuser and (not profile or profile.bidang_pembedahan != 'UPPER GI'):
        messages.error(request, "You do not have permission to add this activity.")
        return redirect('upper_gi_activities')
    
    current_year = datetime.now().year
    existing = UpperGIActivity.objects.filter(year=current_year)
    periods_used = [a.period for a in existing]
    
    if len(periods_used) >= 2:
        messages.error(request, "Both periods for this year are already created.")
        return redirect('upper_gi_activities')
    
    next_period = "Jan-Jun" if "Jan-Jun" not in periods_used else "Jul-Dec"
    
    UpperGIActivity.objects.create(
        period=next_period,
        year=current_year,
        status='not_started'
    )
    
    messages.success(request, f"Activity {next_period} {current_year} created successfully!")
    return redirect('upper_gi_activities')


@login_required
def form_upper_gi(request, activity_id):
    profile = getattr(request.user, 'profile', None)
    
    if not request.user.is_superuser and (not profile or profile.bidang_pembedahan != 'UPPER GI'):
        messages.error(request, "You do not have permission to access this form.")
        return redirect('upper_gi_activities')
    
    activity = get_object_or_404(UpperGIActivity, id=activity_id)
    
    structure_domains = [
        "Availability of specialist and MO (Ensures adequate medical expertise for upper GI surgical procedures)",
        "Availability of paramedics (Supports emergency and perioperative care in upper GI surgery)",
        "Availability of support services (Ensures ancillary services such as imaging and laboratory are accessible for clinical decision-making)",
        "Functioning OT 24 Hours (Ensures continuous operating theatre availability for emergencies and elective cases)",
        "Complete set of surgical instrument (Prevents delays or complications due to missing tools during procedures)"
    ]
    
    process_domains = [
        "Percentage of pre-operative assessment documented (Tracks completeness of patient evaluation prior to upper GI surgery)",
        "Percentage of informed consent taken (Ensures patients are adequately informed and agreement is recorded before surgery)",
        "Percentage of surgical safety checklist (Measures adherence to the WHO Surgical Safety Checklist in upper GI procedures)",
        "Percentage of operation notes documented (Tracks timely and accurate documentation of surgical findings and procedures)",
        "Percentage of post-operative review (Ensures all patients are reviewed and monitored after upper GI surgery)"
    ]
    
    outcome_domains = [
        "Percentage of post-operative complications (Rate of adverse clinical events following upper GI surgical procedures)",
        "Percentage of mortality rate (Rate of deaths occurring within 30 days of upper GI surgery)"
    ]
    
    detail_dict = {}
    all_details = UpperGIDetail.objects.filter(activity=activity)
    for d in all_details:
        key = f"{d.category}_{d.domain_name}"
        detail_dict[key] = {
            'performances': d.performances_value,
            'target': d.target,
            'weight': d.weight,
            'score': d.score,
            'wscore': d.weighted_score,
            'index': d.index
        }
    
    if request.method == 'POST':
        UpperGIDetail.objects.filter(activity=activity).delete()
        
        def save_domain(category, domain_name, i):
            performances = request.POST.get(f'{category}_performances_{i}', '0')
            target = request.POST.get(f'{category}_target_{i}', '0')
            weight = request.POST.get(f'{category}_weight_{i}', '0')
            
            score_f, wscore_f, index_f = calculate_domain_scores(performances, target, weight)

            UpperGIDetail.objects.create(
                activity=activity,
                category=category,
                domain_name=domain_name,
                performances_value=int(performances) if performances else 0,
                target=int(target) if target else 0,
                weight=float(weight) if weight else 0,
                score=score_f,
                weighted_score=wscore_f,
                index=index_f
            )
            
            return Decimal(str(wscore_f))
        
        total_structure = Decimal('0')
        for i, domain in enumerate(structure_domains, start=1):
            total_structure += save_domain('structure', domain, i)
        
        total_process = Decimal('0')
        for i, domain in enumerate(process_domains, start=1):
            total_process += save_domain('process', domain, i)
        
        total_outcome = Decimal('0')
        for i, domain in enumerate(outcome_domains, start=1):
            total_outcome += save_domain('outcome', domain, i)
        
        activity.total_structure = total_structure.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        activity.total_process = total_process.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        activity.total_outcome = total_outcome.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        activity.status = 'completed'
        activity.save()
        
        messages.success(request, 'Data saved successfully!')
        return redirect('upper_gi_activities')
    
    return render(request, "accounts/form_upper_gi.html", {
        "activity": activity,
        "structure_domains": structure_domains,
        "process_domains": process_domains,
        "outcome_domains": outcome_domains,
        "detail_dict": detail_dict,
    })


@login_required
def dashboard_upper_gi(request):
    selected_year = int(request.GET.get('year', datetime.now().year))
    selected_period = request.GET.get('period', 'Jan-Jun')
    
    try:
        activity = UpperGIActivity.objects.get(year=selected_year, period=selected_period)
        total_structure = activity.total_structure
        total_process = activity.total_process
        total_outcome = activity.total_outcome
        overall_index = activity.overall_index
        
        details = UpperGIDetail.objects.filter(activity=activity)
        domain_rows = []
        for d in details:
            domain_rows.append({
                'category': d.category.capitalize(),
                'domain': d.domain_name,
                'performances_value': d.performances_value,
                'target': d.target,
                'weight': d.weight,
                'score': d.score,
                'weighted_score': d.weighted_score,
                'index': d.index
            })
    except UpperGIActivity.DoesNotExist:
        total_structure = 0
        total_process = 0
        total_outcome = 0
        overall_index = 0
        domain_rows = []
    
    years = UpperGIActivity.objects.values_list('year', flat=True).distinct().order_by('-year')
    if not years:
        years = [datetime.now().year]
    
    return render(request, 'accounts/dashboard_upper_gi.html', {
        'total_structure': total_structure,
        'total_process': total_process,
        'total_outcome': total_outcome,
        'overall_index': overall_index,
        'domain_rows': domain_rows,
        'years': years,
        'selected_year': selected_year,
        'selected_period': selected_period,
        'bar_labels': '[]',
        'bar_values': '[]'
    })


# =============================================
# GS BREAST & ENDOCRINE
# =============================================
@login_required
def gsbreast_endocrine(request):
    return render(request, 'accounts/gsbreast_endocrine.html')


@login_required
def gsbreast_endocrine_activities(request):
    year = datetime.now().year
    activities = SurgeryActivity.objects.filter(
        fraternity="General Surgery Breast and Endocrine",
        year=year
    ).annotate(
        period_order=Case(
            When(period='Jan-Jun', then=1),
            When(period='Jul-Dec', then=2),
            default=3,
            output_field=IntegerField()
        )
    ).order_by('period_order')

    return render(request, 'accounts/gsbreast_endocrine_activities.html', {
        'activities': activities,
        'year': year,
    })


@login_required
def add_gsbreast_endocrine_activity(request):
    profile = getattr(request.user, 'profile', None)
    
    # ✅ STRICT CHECK (superadmin bypasses)
    if not request.user.is_superuser and (not profile or profile.bidang_pembedahan != 'GENERAL SURGERY BREAST AND ENDOCRINE'):
        messages.error(request, "You do not have permission to add this activity.")
        return redirect("gsbreast_endocrine_activities")
    
    year = datetime.now().year
    existing = SurgeryActivity.objects.filter(
        fraternity="General Surgery Breast and Endocrine",
        year=year
    ).count()

    if existing == 0:
        period = "Jan-Jun"
    elif existing == 1:
        period = "Jul-Dec"
    else:
        messages.error(request, "The activities for this year are already complete.")
        return redirect("gsbreast_endocrine_activities")

    activity, created = SurgeryActivity.objects.get_or_create(
        fraternity="General Surgery Breast and Endocrine",
        year=year,
        period=period
    )
    activity.users.add(request.user)
    messages.success(request, f"You have been added to the activity {period} {year}.")
    return redirect("gsbreast_endocrine_activities")


@login_required
def form_gsbreast_endocrine(request, activity_id):
    profile = getattr(request.user, 'profile', None)
    
    # ✅ STRICT CHECK (superadmin bypasses)
    if not request.user.is_superuser and (not profile or profile.bidang_pembedahan != 'GENERAL SURGERY BREAST AND ENDOCRINE'):
        messages.error(request, "You do not have permission to access this form.")
        return redirect('gsbreast_endocrine_activities')
    
    activity = get_object_or_404(SurgeryActivity, id=activity_id)

    structure_domains = [
        "Number of FTE consultant breast/endocrine surgeons (Ensures sufficient specialist capacity to manage breast and endocrine surgical cases)",
        "Availability of breast imaging facilities — mammography, ultrasound (Supports accurate diagnosis and pre-surgical planning for breast conditions)",
        "Dedicated breast clinic space (Provides a focused environment for assessment and follow-up of breast and endocrine patients)",
        "Availability of biopsy equipment (Enables tissue sampling for definitive diagnosis of breast and endocrine lesions)",
        "Pathology service for tissue diagnosis (Supports timely histological confirmation to guide surgical management)",
        "MDT meeting structure for breast/endocrine cases (Facilitates multidisciplinary decision-making for complex or oncological cases)",
        "Operating theatre with specialized equipment (Ensures safe and effective execution of breast and endocrine surgical procedures)",
        "Availability of registered nurses trained in breast care (Supports safe perioperative care and patient education in breast surgery)",
        "Clinical guidelines for breast and endocrine conditions (Standardizes management and reduces variation in clinical practice)",
        "Documentation templates for breast/endocrine procedures (Promotes consistent and complete recording of clinical findings and interventions)"
    ]
    
    process_domains = [
        "Percentage of breast cancer cases discussed in MDT (Ensures all oncology cases receive multidisciplinary review before treatment)",
        "Percentage of patients with documented informed consent (Verifies that patients are informed and agreement is recorded prior to surgery)",
        "Percentage of surgical safety checklist compliance (Measures adherence to WHO safety protocols during breast and endocrine procedures)",
        "Percentage of pre-operative assessment completed (Tracks thorough evaluation of patient fitness and readiness before surgery)",
        "Percentage of post-operative review documented (Ensures clinical findings and recovery progress are recorded after surgery)",
        "Time from diagnosis to surgery (Measures efficiency and timeliness of the surgical pathway from diagnosis to intervention)",
        "Percentage of breast cancer patients with timely treatment (Tracks adherence to target treatment timelines to optimize oncology outcomes)"
    ]
    
    outcome_domains = [
        "Percentage of post-operative complications (Rate of adverse events following breast and endocrine surgical procedures)",
        "30-day mortality rate for breast/endocrine surgery (Rate of deaths within 30 days of breast or endocrine surgical intervention)",
        "Patient satisfaction score (Measures patient-reported experience and satisfaction with breast and endocrine surgical care)",
        "Re-operation rate (Proportion of patients requiring a second surgical intervention due to complications or incomplete resection)",
        "Cancer recurrence rate (Rate of disease recurrence following surgical treatment for breast or endocrine malignancy)"
    ]

    details = SurgeryActivityDetail.objects.filter(activity=activity)
    detail_dict = {}
    for d in details:
        key = f"{d.category}_{d.domain}"
        detail_dict[key] = {
            "performances": d.performances_value,
            "target": d.target,
            "weight": d.weight,
            "score": d.score,
            "wscore": d.weighted_score,
            "index": d.index
        }

    if request.method == "POST":
        SurgeryActivityDetail.objects.filter(activity=activity).delete()

        def save_category(category_name, domains):
            total = Decimal('0')
            for i, domain in enumerate(domains, start=1):
                performances = request.POST.get(f"{category_name}_performances_{i}", "0")
                target = request.POST.get(f"{category_name}_target_{i}", "0")
                weight = request.POST.get(f"{category_name}_weight_{i}", "0")

                score_f, wscore_f, index_f = calculate_domain_scores(performances, target, weight)

                SurgeryActivityDetail.objects.create(
                    activity=activity,
                    category=category_name,
                    domain=domain,
                    performances_value=int(performances) if performances else 0,
                    target=int(target) if target else 0,
                    weight=float(weight) if weight else 0,
                    score=score_f,
                    weighted_score=wscore_f,
                    index=index_f
                )
                total += Decimal(str(wscore_f))
            return float(total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))

        activity.total_structure = save_category("structure", structure_domains)
        activity.total_process = save_category("process", process_domains)
        activity.total_outcome = save_category("outcome", outcome_domains)
        activity.status = "done"
        activity.save()

        messages.success(request, "Data has been successfully saved.")
        return redirect('gsbreast_endocrine_activities')

    return render(request, "accounts/form_gsbreast_endocrine.html", {
        "activity": activity,
        "structure_domains": structure_domains,
        "process_domains": process_domains,
        "outcome_domains": outcome_domains,
        "detail_dict": detail_dict,
    })


@login_required
def dashboard_gsbreast_endocrine(request):
    selected_year = int(request.GET.get('year', datetime.now().year))
    selected_period = request.GET.get('period', 'Jan-Jun')

    activities = SurgeryActivity.objects.filter(
        fraternity="General Surgery Breast and Endocrine",
        status="done",
        year=selected_year,
        period=selected_period
    )

    if not activities.exists():
        context = {
            "selected_year": selected_year,
            "selected_period": selected_period,
            "years": list(range(2020, datetime.now().year + 2)),
            "total_structure_raw": 0,
            "total_process_raw": 0,
            "total_outcome_raw": 0,
            "total_structure": 0,
            "total_process": 0,
            "total_outcome": 0,
            "overall_index": 0,
            "domain_rows": []
        }
        return render(request, "accounts/dashboard_gsbreast_endocrine.html", context)

    activity = activities.first()
    details = SurgeryActivityDetail.objects.filter(activity=activity)

    total_structure_raw = sum(details.filter(category="structure").values_list("weighted_score", flat=True)) or 0.0
    total_process_raw = sum(details.filter(category="process").values_list("weighted_score", flat=True)) or 0.0
    total_outcome_raw = sum(details.filter(category="outcome").values_list("weighted_score", flat=True)) or 0.0

    total_structure_raw = min(float(total_structure_raw), 1.0)
    total_process_raw = min(float(total_process_raw), 1.0)
    total_outcome_raw = min(float(total_outcome_raw), 1.0)

    total_structure = total_structure_raw * 0.3
    total_process = total_process_raw * 0.4
    total_outcome = total_outcome_raw * 0.3

    overall_index = total_structure + total_process + total_outcome
    overall_index = min(overall_index, 1.0)

    domain_rows = []
    for d in details:
        domain_rows.append({
            "category": d.category.capitalize(),
            "domain": d.domain,
            "performances_value": d.performances_value,
            "target": d.target,
            "weight": d.weight,
            "score": d.score,
            "weighted_score": d.weighted_score,
            "index": d.index,
        })

    context = {
        "selected_year": selected_year,
        "selected_period": selected_period,
        "years": list(range(2020, datetime.now().year + 2)),
        "total_structure_raw": round(total_structure_raw, 2),
        "total_process_raw": round(total_process_raw, 2),
        "total_outcome_raw": round(total_outcome_raw, 2),
        "total_structure": round(total_structure, 2),
        "total_process": round(total_process, 2),
        "total_outcome": round(total_outcome, 2),
        "overall_index": round(overall_index, 2),
        "domain_rows": domain_rows,
    }

    return render(request, "accounts/dashboard_gsbreast_endocrine.html", context)






@login_required
def gsvascular(request):
    return render(request, 'accounts/gsvascular.html')


@login_required
def gsvascular_activities(request):
    year = datetime.now().year
    activities = SurgeryActivity.objects.filter(
        fraternity="General Surgery Vascular",
        year=year
    ).annotate(
        period_order=Case(
            When(period='Jan-Jun', then=1),
            When(period='Jul-Dec', then=2),
            default=3,
            output_field=IntegerField()
        )
    ).order_by('period_order')

    return render(request, 'accounts/gsvascular_activities.html', {
        'activities': activities,
        'year': year,
    })


@login_required
def add_gsvascular_activity(request):
    profile = getattr(request.user, 'profile', None)

    # same strict permission check used elsewhere (superadmin bypasses)
    if not request.user.is_superuser and (not profile or profile.bidang_pembedahan != 'GENERAL SURGERY VASCULAR'):
        messages.error(request, "You do not have permission to add this activity.")
        return redirect('gsvascular_activities')

    current_year = datetime.now().year
    existing = SurgeryActivity.objects.filter(
        fraternity="General Surgery Vascular",
        year=current_year
    ).count()

    if existing == 0:
        period = "Jan-Jun"
    elif existing == 1:
        period = "Jul-Dec"
    else:
        messages.error(request, "The activities for this year are already complete.")
        return redirect('gsvascular_activities')

    activity, created = SurgeryActivity.objects.get_or_create(
        fraternity="General Surgery Vascular",
        year=current_year,
        period=period,
        defaults={'status': 'not_started'}
    )
    activity.users.add(request.user)
    messages.success(request, f"You have been added to the activity {period} {current_year}.")
    return redirect('gsvascular_activities')


@login_required
def form_gsvascular(request, activity_id):
    profile = getattr(request.user, 'profile', None)
    if not request.user.is_superuser and (not profile or profile.bidang_pembedahan != 'GENERAL SURGERY VASCULAR'):
        messages.error(request, "You do not have permission to access this form.")
        return redirect('gsvascular_activities')

    activity = get_object_or_404(SurgeryActivity, id=activity_id)

    structure_domains = [
        "Number of FTE consultant vascular surgeons (Ensures adequate specialist capacity for managing complex vascular surgical cases)",
        "Dedicated vascular operating theatre (Provides a safe and equipped environment for open and endovascular procedures)",
        "Availability of endovascular intervention suite (Enables minimally invasive treatment of vascular conditions with imaging support)",
        "Duplex ultrasound availability (Supports non-invasive diagnosis and surveillance of vascular disease)",
        "Hybrid theatre or catheterisation lab access (Facilitates combined open and endovascular procedures in a single setting)",
        "Availability of vascular trained scrub nurses and theatre staff (Ensures safe intraoperative support for vascular surgical procedures)",
        "Clinical protocols for common vascular emergencies (Standardizes management of acute limb ischaemia, ruptured aneurysm and major haemorrhage)",
        "Access to vascular imaging — CT angiography, MR angiography (Supports accurate pre-operative planning and diagnosis of vascular conditions)"
    ]
    process_domains = [
        "Percentage of vascular patients with documented pre-operative risk assessment (Tracks completeness of evaluation before vascular surgery)",
        "MDT review rate for complex vascular cases (Measures proportion of complex cases discussed in a multidisciplinary team setting)",
        "Adherence to surgical safety checklist for vascular procedures (Tracks compliance with WHO safety protocols during vascular operations)",
        "Percentage of elective AAA repairs meeting size threshold criteria (Monitors appropriateness of patient selection for elective intervention)",
        "Time from admission to theatre for acute limb ischaemia (Measures responsiveness of the vascular surgical service for emergencies)",
        "Percentage of post-operative review documented (Ensures patients are assessed and clinical findings recorded after vascular surgery)"
    ]
    outcome_domains = [
        "30-day mortality rate for major vascular surgery (Rate of deaths within 30 days of open or endovascular vascular intervention)",
        "Major amputation rate (Proportion of patients requiring limb amputation following vascular surgical management)",
        "Graft patency rate at 12 months (Proportion of vascular grafts remaining patent one year after surgical or endovascular repair)",
        "Post-operative complication rate (Rate of adverse events including bleeding, wound infection and graft complications)",
        "Readmission rate within 30 days (Proportion of patients requiring hospital readmission within 30 days of vascular surgery)"
    ]

    details = SurgeryActivityDetail.objects.filter(activity=activity)
    detail_dict = {}
    for d in details:
        key = f"{d.category}_{d.domain}"
        detail_dict[key] = {
            "performances": d.performances_value,
            "target": d.target,
            "weight": d.weight,
            "score": d.score,
            "wscore": d.weighted_score,
            "index": d.index
        }

    if request.method == "POST":
        SurgeryActivityDetail.objects.filter(activity=activity).delete()

        def save_category(category_name, domains):
            total = Decimal('0')
            for i, domain in enumerate(domains, start=1):
                performances = request.POST.get(f"{category_name}_performances_{i}", "0")
                target = request.POST.get(f"{category_name}_target_{i}", "0")
                weight = request.POST.get(f"{category_name}_weight_{i}", "0")
                score_f, wscore_f, index_f = calculate_domain_scores(performances, target, weight)
                SurgeryActivityDetail.objects.create(
                    activity=activity,
                    category=category_name,
                    domain=domain,
                    performances_value=int(performances) if performances else 0,
                    target=int(target) if target else 0,
                    weight=float(weight) if weight else 0,
                    score=score_f,
                    weighted_score=wscore_f,
                    index=index_f
                )
                total += Decimal(str(wscore_f))
            return float(total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))

        activity.total_structure = save_category("structure", structure_domains)
        activity.total_process = save_category("process", process_domains)
        activity.total_outcome = save_category("outcome", outcome_domains)
        activity.status = "done"
        activity.save()

        messages.success(request, "Data has been successfully saved.")
        return redirect('gsvascular_activities')

    return render(request, "accounts/form_gsvascular.html", {
        "activity": activity,
        "structure_domains": structure_domains,
        "process_domains": process_domains,
        "outcome_domains": outcome_domains,
        "detail_dict": detail_dict,
    })


@login_required
def dashboard_gsvascular(request):
    selected_year = int(request.GET.get('year', datetime.now().year))
    selected_period = request.GET.get('period', 'Jan-Jun')

    activities = SurgeryActivity.objects.filter(
        fraternity="General Surgery Vascular",
        status="done",
        year=selected_year,
        period=selected_period
    )

    if not activities.exists():
        context = {
            "selected_year": selected_year,
            "selected_period": selected_period,
            "years": list(range(2020, datetime.now().year + 2)),
            "total_structure_raw": 0,
            "total_process_raw": 0,
            "total_outcome_raw": 0,
            "total_structure": 0,
            "total_process": 0,
            "total_outcome": 0,
            "overall_index": 0,
            "domain_rows": [],
            "bar_labels": "[]",
            "bar_values": "[]",
        }
        return render(request, "accounts/dashboard_gsvascular.html", context)

    activity = activities.first()
    details = SurgeryActivityDetail.objects.filter(activity=activity)

    total_structure_raw = sum(details.filter(category="structure").values_list("weighted_score", flat=True)) or 0.0
    total_process_raw = sum(details.filter(category="process").values_list("weighted_score", flat=True)) or 0.0
    total_outcome_raw = sum(details.filter(category="outcome").values_list("weighted_score", flat=True)) or 0.0

    total_structure_raw = min(float(total_structure_raw), 1.0)
    total_process_raw = min(float(total_process_raw), 1.0)
    total_outcome_raw = min(float(total_outcome_raw), 1.0)

    total_structure = total_structure_raw * 0.3
    total_process = total_process_raw * 0.4
    total_outcome = total_outcome_raw * 0.3

    overall_index = min(total_structure + total_process + total_outcome, 1.0)

    domain_rows = []
    for d in details:
        domain_rows.append({
            "category": d.category.capitalize(),
            "domain": d.domain,
            "performances_value": d.performances_value,
            "target": d.target,
            "weight": d.weight,
            "score": d.score,
            "weighted_score": d.weighted_score,
            "index": d.index,
        })

    years = list(range(2020, datetime.now().year + 2))

    context = {
        "total_structure_raw": round(total_structure_raw, 2),
        "total_process_raw": round(total_process_raw, 2),
        "total_outcome_raw": round(total_outcome_raw, 2),
        "total_structure": round(total_structure, 2),
        "total_process": round(total_process, 2),
        "total_outcome": round(total_outcome, 2),
        "overall_index": round(overall_index, 2),
        "domain_rows": domain_rows,
        "years": years,
        "selected_year": selected_year,
        "selected_period": selected_period,
        "bar_labels": "[]",
        "bar_values": "[]",
    }

    return render(request, "accounts/dashboard_gsvascular.html", context)

# =============================================
# OTHER SURGICAL FRATERNITIES (PLACEHOLDER)
# =============================================

@login_required
def gshepatobiliary(request):
    return render(request, 'accounts/gshepatobiliary.html')


@login_required
def gshepatobiliary_activities(request):
    year = datetime.now().year
    activities = SurgeryActivity.objects.filter(
        fraternity="General Surgery Hepatobiliary",
        year=year
    ).annotate(
        period_order=Case(
            When(period='Jan-Jun', then=1),
            When(period='Jul-Dec', then=2),
            default=3,
            output_field=IntegerField()
        )
    ).order_by('period_order')
    return render(request, 'accounts/gshepatobiliary_activities.html', {
        'activities': activities,
        'year': year,
    })


@login_required
def add_gshepatobiliary_activity(request):
    profile = getattr(request.user, 'profile', None)
    if not request.user.is_superuser and (not profile or profile.bidang_pembedahan != 'GENERAL SURGERY HEPATOBILIARY'):
        messages.error(request, "You do not have permission to add this activity.")
        return redirect('gshepatobiliary_activities')

    current_year = datetime.now().year
    existing = SurgeryActivity.objects.filter(
        fraternity="General Surgery Hepatobiliary",
        year=current_year
    ).count()

    if existing == 0:
        period = "Jan-Jun"
    elif existing == 1:
        period = "Jul-Dec"
    else:
        messages.error(request, "The activities for this year are already complete.")
        return redirect('gshepatobiliary_activities')

    activity, created = SurgeryActivity.objects.get_or_create(
        fraternity="General Surgery Hepatobiliary",
        year=current_year,
        period=period,
        defaults={'status': 'not_started'}
    )
    activity.users.add(request.user)
    messages.success(request, f"Activity {period} {current_year} created successfully!")
    return redirect('gshepatobiliary_activities')

@login_required
def delete_gshepatobiliary_activity(request, activity_id):
    profile = getattr(request.user, 'profile', None)
    
    # Semak akses (hanya yang sah atau superuser boleh padam)
    if not request.user.is_superuser and (not profile or profile.bidang_pembedahan != 'GENERAL SURGERY HEPATOBILIARY'):
        messages.error(request, "You do not have permission to delete this activity.")
        return redirect('gshepatobiliary_activities')

    # Cari aktiviti dan padam
    activity = get_object_or_404(SurgeryActivity, id=activity_id)
    activity.delete()
    
    messages.success(request, "Activity has been successfully deleted/reset.")
    return redirect('gshepatobiliary_activities')


@login_required
def form_gshepatobiliary(request, activity_id):
    profile = getattr(request.user, 'profile', None)
    if not request.user.is_superuser and (not profile or profile.bidang_pembedahan != 'GENERAL SURGERY HEPATOBILIARY'):
        messages.error(request, "You do not have permission to access this form.")
        return redirect('gshepatobiliary_activities')

    activity = get_object_or_404(SurgeryActivity, id=activity_id)

    # Parameter Terbaru dari Excel V2 (28 Ogos)
    structure_domains = [
        "Annual campaign of HCC awareness",
        "Presence of Hepatitis screening for high-risk patient in primary health care",
        "Development of HCC guidelines for Malaysia.",
        "The percentage of the state (except Perlis) has HPB centers with minimal 2 HPB surgeons",
        "Percentage of HPB Surgery Center which are well equipped",
        "Percentage of HPB Surgery center with min 2 HPB Surgeons",
        "Percentage of budget for HPB surgery that being proposed is being allocated",
        "Availability of NCR, NTRC and MyOrganMatch"
    ]
    process_domains = [
        "Presence of referral pathway of HCC patient to HPB surgery center",
        "Percentage of HPB surgery center with MDT discussion for HCC",
        "Percentage of referral to anaesthetist for pre-op assessment of pt undergoing surgery for HCC",
        "Percentage of informed consent by specialist for HCC surgery",
        "Percentage of SSSL check list compliancy for HCC surgery",
        "Percentage of ASA score assessment",
        "Percentage of POMR reporting"
    ]
    outcome_domains = [
        "Percentage waiting time for surgery <1 month",
        "Reoperation Rate for HCC elective surgery",
        "30-Day Mortality Rate",
        "Surgical Site Infection rate",
        "Percentage of complaints received",
        "Time of referral to appointment within 2/52 - for HPB surgery clinic"
    ]

    details = SurgeryActivityDetail.objects.filter(activity=activity)
    detail_dict = {}
    for d in details:
        key = f"{d.category}_{d.domain}"
        detail_dict[key] = {
            "performances": d.performances_value,
            "denominator": d.denominator,  # ✅ WAJIB ADA UNTUK FORMULA BAHARU
            "target": d.target,
            "weight": d.weight,
            "score": d.score,
            "wscore": d.weighted_score,
            "index": d.index
        }

    if request.method == "POST":
        SurgeryActivityDetail.objects.filter(activity=activity).delete()

        def save_category(category_name, domains):
            total = Decimal('0')
            for i, domain in enumerate(domains, start=1):
                performances = request.POST.get(f"{category_name}_performances_{i}", "0")
                denominator = request.POST.get(f"{category_name}_denominator_{i}", "0")
                target = request.POST.get(f"{category_name}_target_{i}", "0")
                weight = request.POST.get(f"{category_name}_weight_{i}", "0")
                
                try: num_d = Decimal(str(performances))
                except: num_d = Decimal('0')
                try: den_d = Decimal(str(denominator))
                except: den_d = Decimal('0')
                try: wgt_d = Decimal(str(weight))
                except: wgt_d = Decimal('0')
                
                if den_d > 0:
                    score_d = (num_d / den_d) * Decimal('100')
                    wscore_d = (num_d / den_d) * wgt_d
                    index_d = num_d / den_d
                else:
                    score_d = Decimal('0')
                    wscore_d = Decimal('0')
                    index_d = Decimal('0')
                    
                score_f = float(score_d.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
                wscore_f = float(wscore_d.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
                index_f = float(index_d.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))

                SurgeryActivityDetail.objects.create(
                    activity=activity,
                    category=category_name,
                    domain=domain,
                    performances_value=int(performances) if performances else 0,
                    denominator=int(denominator) if denominator else 0, # ✅ SIMPAN DENOMINATOR
                    target=int(target) if target else 0,
                    weight=float(weight) if weight else 0,
                    score=score_f,
                    weighted_score=wscore_f,
                    index=index_f
                )
                total += Decimal(str(wscore_f))
            return float(total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))

        activity.total_structure = save_category("structure", structure_domains)
        activity.total_process = save_category("process", process_domains)
        activity.total_outcome = save_category("outcome", outcome_domains)
        activity.status = "completed"
        activity.save()

        messages.success(request, "Data has been successfully saved.")
        return redirect('gshepatobiliary_activities')

    return render(request, "accounts/form_gshepatobiliary.html", {
        "activity": activity,
        "structure_domains": structure_domains,
        "process_domains": process_domains,
        "outcome_domains": outcome_domains,
        "detail_dict": detail_dict,
    })

    if request.method == "POST":
        SurgeryActivityDetail.objects.filter(activity=activity).delete()

        def save_category(category_name, domains):
            total = Decimal('0')
            for i, domain in enumerate(domains, start=1):
                performances = request.POST.get(f"{category_name}_performances_{i}", "0")
                target = request.POST.get(f"{category_name}_target_{i}", "0")
                weight = request.POST.get(f"{category_name}_weight_{i}", "0")
                score_f, wscore_f, index_f = calculate_domain_scores(performances, target, weight)
                SurgeryActivityDetail.objects.create(
                    activity=activity,
                    category=category_name,
                    domain=domain,
                    performances_value=int(performances) if performances else 0,
                    target=int(target) if target else 0,
                    weight=float(weight) if weight else 0,
                    score=score_f,
                    weighted_score=wscore_f,
                    index=index_f
                )
                total += Decimal(str(wscore_f))
            return float(total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))

        activity.total_structure = save_category("structure", structure_domains)
        activity.total_process = save_category("process", process_domains)
        activity.total_outcome = save_category("outcome", outcome_domains)
        activity.status = "done"
        activity.save()

        messages.success(request, "Data has been successfully saved.")
        return redirect('gshepatobiliary_activities')

    return render(request, "accounts/form_gshepatobiliary.html", {
        "activity": activity,
        "structure_domains": structure_domains,
        "process_domains": process_domains,
        "outcome_domains": outcome_domains,
        "detail_dict": detail_dict,
    })


@login_required
def dashboard_gshepatobiliary(request):
    selected_year = int(request.GET.get('year', datetime.now().year))
    selected_period = request.GET.get('period', 'Jan-Jun')

    activities = SurgeryActivity.objects.filter(
        fraternity="General Surgery Hepatobiliary",
        status="completed",
        year=selected_year,
        period=selected_period
    )

    if not activities.exists():
        context = {
            "selected_year": selected_year,
            "selected_period": selected_period,
            "years": list(range(2020, datetime.now().year + 2)),
            "total_structure_raw": 0,
            "total_process_raw": 0,
            "total_outcome_raw": 0,
            "total_structure": 0,
            "total_process": 0,
            "total_outcome": 0,
            "overall_index": 0,
            "domain_rows": [],
        }
        return render(request, "accounts/dashboard_gshepatobiliary.html", context)

    activity = activities.first()
    details = SurgeryActivityDetail.objects.filter(activity=activity)

    total_structure_raw = sum(details.filter(category="structure").values_list("weighted_score", flat=True)) or 0.0
    total_process_raw   = sum(details.filter(category="process").values_list("weighted_score", flat=True)) or 0.0
    total_outcome_raw   = sum(details.filter(category="outcome").values_list("weighted_score", flat=True)) or 0.0

    total_structure_raw = min(float(total_structure_raw), 1.0)
    total_process_raw   = min(float(total_process_raw), 1.0)
    total_outcome_raw   = min(float(total_outcome_raw), 1.0)

    total_structure = total_structure_raw * 0.5
    total_process   = total_process_raw   * 0.2
    total_outcome   = total_outcome_raw   * 0.3
    overall_index   = min(total_structure + total_process + total_outcome, 1.0)

    domain_rows = []
    for d in details:
        domain_rows.append({
            "category": d.category.capitalize(),
            "domain": d.domain,
            "performances_value": d.performances_value,
            "target": d.target,
            "weight": d.weight,
            "score": d.score,
            "weighted_score": d.weighted_score,
            "index": d.index,
        })

    context = {
        "total_structure_raw": round(total_structure_raw, 2),
        "total_process_raw":   round(total_process_raw, 2),
        "total_outcome_raw":   round(total_outcome_raw, 2),
        "total_structure":     round(total_structure, 2),
        "total_process":       round(total_process, 2),
        "total_outcome":       round(total_outcome, 2),
        "overall_index":       round(overall_index, 2),
        "domain_rows":         domain_rows,
        "years":               list(range(2020, datetime.now().year + 2)),
        "selected_year":       selected_year,
        "selected_period":     selected_period,
    }
    return render(request, "accounts/dashboard_gshepatobiliary.html", context)


@login_required
def gsthoracic(request):
    return render(request, 'accounts/gsthoracic.html')


@login_required
def gsthoracic_activities(request):
    year = datetime.now().year
    activities = SurgeryActivity.objects.filter(
        fraternity="General Surgery Thoracic",
        year=year
    ).annotate(
        period_order=Case(
            When(period='Jan-Jun', then=1),
            When(period='Jul-Dec', then=2),
            default=3,
            output_field=IntegerField()
        )
    ).order_by('period_order')
    return render(request, 'accounts/gsthoracic_activities.html', {
        'activities': activities,
        'year': year,
    })


@login_required
def add_gsthoracic_activity(request):
    profile = getattr(request.user, 'profile', None)
    if not request.user.is_superuser and (not profile or profile.bidang_pembedahan != 'GENERAL SURGERY THORACIC'):
        messages.error(request, "You do not have permission to add this activity.")
        return redirect('gsthoracic_activities')

    current_year = datetime.now().year
    existing = SurgeryActivity.objects.filter(
        fraternity="General Surgery Thoracic",
        year=current_year
    ).count()

    if existing == 0:
        period = "Jan-Jun"
    elif existing == 1:
        period = "Jul-Dec"
    else:
        messages.error(request, "The activities for this year are already complete.")
        return redirect('gsthoracic_activities')

    activity, created = SurgeryActivity.objects.get_or_create(
        fraternity="General Surgery Thoracic",
        year=current_year,
        period=period,
        defaults={'status': 'not_started'}
    )
    activity.users.add(request.user)
    messages.success(request, f"Activity {period} {current_year} created successfully!")
    return redirect('gsthoracic_activities')


@login_required
def form_gsthoracic(request, activity_id):
    profile = getattr(request.user, 'profile', None)
    if not request.user.is_superuser and (not profile or profile.bidang_pembedahan != 'GENERAL SURGERY THORACIC'):
        messages.error(request, "You do not have permission to access this form.")
        return redirect('gsthoracic_activities')

    activity = get_object_or_404(SurgeryActivity, id=activity_id)

    structure_domains = [
        "Number of FTE consultant thoracic surgeons (Ensures sufficient specialist availability for managing chest and pulmonary surgical cases)",
        "Dedicated thoracic operating theatre (Provides a safe and appropriately equipped environment for thoracic procedures)",
        "Availability of VATS equipment — video-assisted thoracoscopic surgery (Enables minimally invasive chest surgery with improved patient recovery)",
        "Pulmonary function testing facilities (Supports pre-operative respiratory assessment to guide surgical decision-making)",
        "Thoracic ICU/HDU beds availability (Ensures adequate critical care capacity for post-thoracic surgery monitoring and recovery)",
    ]
    process_domains = [
        "MDT meetings for thoracic oncology (Ensures multidisciplinary review of lung and thoracic cancer cases before treatment)",
        "Pre-operative staging and imaging protocol compliance (Tracks completeness of radiological workup before thoracic surgery)",
        "Intraoperative bronchoscopy utilization (Measures use of airway visualization during thoracic procedures for safety and accuracy)",
        "Adherence to ERATS protocol — enhanced recovery after thoracic surgery (Tracks compliance with evidence-based recovery pathways to reduce length of stay)",
        "Post-operative chest physiotherapy protocol adherence (Ensures respiratory rehabilitation is delivered to reduce pulmonary complications)",
    ]
    outcome_domains = [
        "30-day surgical mortality rate (Rate of deaths within 30 days of thoracic surgical intervention)",
        "Rate of prolonged air leak greater than 7 days (Tracks a key post-operative complication following pulmonary resection)",
        "Post-operative pulmonary complication rate (Rate of respiratory adverse events such as pneumonia or atelectasis after thoracic surgery)",
        "Mean length of hospital stay (Average inpatient duration after thoracic surgery as an indicator of recovery efficiency)",
        "Readmission rate within 30 days (Proportion of patients requiring hospital readmission within 30 days of thoracic surgery)",
    ]

    details = SurgeryActivityDetail.objects.filter(activity=activity)
    detail_dict = {}
    for d in details:
        key = f"{d.category}_{d.domain}"
        detail_dict[key] = {
            "performances": d.performances_value,
            "target": d.target,
            "weight": d.weight,
            "score": d.score,
            "wscore": d.weighted_score,
            "index": d.index
        }

    if request.method == "POST":
        SurgeryActivityDetail.objects.filter(activity=activity).delete()

        def save_category(category_name, domains):
            total = Decimal('0')
            for i, domain in enumerate(domains, start=1):
                performances = request.POST.get(f"{category_name}_performances_{i}", "0")
                target = request.POST.get(f"{category_name}_target_{i}", "0")
                weight = request.POST.get(f"{category_name}_weight_{i}", "0")
                score_f, wscore_f, index_f = calculate_domain_scores(performances, target, weight)
                SurgeryActivityDetail.objects.create(
                    activity=activity,
                    category=category_name,
                    domain=domain,
                    performances_value=int(performances) if performances else 0,
                    target=int(target) if target else 0,
                    weight=float(weight) if weight else 0,
                    score=score_f,
                    weighted_score=wscore_f,
                    index=index_f
                )
                total += Decimal(str(wscore_f))
            return float(total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))

        activity.total_structure = save_category("structure", structure_domains)
        activity.total_process   = save_category("process", process_domains)
        activity.total_outcome   = save_category("outcome", outcome_domains)
        activity.status = "done"
        activity.save()

        messages.success(request, "Data has been successfully saved.")
        return redirect('gsthoracic_activities')

    return render(request, "accounts/form_gsthoracic.html", {
        "activity": activity,
        "structure_domains": structure_domains,
        "process_domains": process_domains,
        "outcome_domains": outcome_domains,
        "detail_dict": detail_dict,
    })


@login_required
def dashboard_gsthoracic(request):
    selected_year   = int(request.GET.get('year', datetime.now().year))
    selected_period = request.GET.get('period', 'Jan-Jun')

    activities = SurgeryActivity.objects.filter(
        fraternity="General Surgery Thoracic",
        status="done",
        year=selected_year,
        period=selected_period
    )

    if not activities.exists():
        context = {
            "selected_year": selected_year,
            "selected_period": selected_period,
            "years": list(range(2020, datetime.now().year + 2)),
            "total_structure_raw": 0,
            "total_process_raw": 0,
            "total_outcome_raw": 0,
            "total_structure": 0,
            "total_process": 0,
            "total_outcome": 0,
            "overall_index": 0,
            "domain_rows": [],
        }
        return render(request, "accounts/dashboard_gsthoracic.html", context)

    activity = activities.first()
    details  = SurgeryActivityDetail.objects.filter(activity=activity)

    total_structure_raw = min(float(sum(details.filter(category="structure").values_list("weighted_score", flat=True)) or 0.0), 1.0)
    total_process_raw   = min(float(sum(details.filter(category="process").values_list("weighted_score", flat=True)) or 0.0), 1.0)
    total_outcome_raw   = min(float(sum(details.filter(category="outcome").values_list("weighted_score", flat=True)) or 0.0), 1.0)

    total_structure = total_structure_raw * 0.3
    total_process   = total_process_raw   * 0.4
    total_outcome   = total_outcome_raw   * 0.3
    overall_index   = min(total_structure + total_process + total_outcome, 1.0)

    domain_rows = [{
        "category": d.category.capitalize(),
        "domain": d.domain,
        "performances_value": d.performances_value,
        "target": d.target,
        "weight": d.weight,
        "score": d.score,
        "weighted_score": d.weighted_score,
        "index": d.index,
    } for d in details]

    context = {
        "total_structure_raw": round(total_structure_raw, 2),
        "total_process_raw":   round(total_process_raw, 2),
        "total_outcome_raw":   round(total_outcome_raw, 2),
        "total_structure":     round(total_structure, 2),
        "total_process":       round(total_process, 2),
        "total_outcome":       round(total_outcome, 2),
        "overall_index":       round(overall_index, 2),
        "domain_rows":         domain_rows,
        "years":               list(range(2020, datetime.now().year + 2)),
        "selected_year":       selected_year,
        "selected_period":     selected_period,
    }
    return render(request, "accounts/dashboard_gsthoracic.html", context)


@login_required
def gstrauma(request):
    return render(request, 'accounts/gstrauma.html')

@login_required
def orthopaedic(request):
    return render(request, 'accounts/orthopaedic.html')

@login_required
def neurosurgery(request):
    return render(request, 'accounts/neurosurgery.html')

@login_required
def urology(request):
    return render(request, 'accounts/urology.html')

# =============================================
# PAEDIATRIC SURGERY
# =============================================
@login_required
def paediatric(request):
    return render(request, 'accounts/paediatric.html')

@login_required
def paediatric_activities(request):
    year = datetime.now().year
    activities = SurgeryActivity.objects.filter(
        fraternity="Paediatric Surgery",
        year=year
    ).annotate(
        period_order=Case(
            When(period='Jan-Jun', then=1),
            When(period='Jul-Dec', then=2),
            default=3,
            output_field=IntegerField()
        )
    ).order_by('period_order')

    return render(request, 'accounts/paediatric_activities.html', {
        'activities': activities,
        'year': year,
    })

@login_required
def add_paediatric_activity(request):
    profile = getattr(request.user, 'profile', None)
    
    if not request.user.is_superuser and (not profile or profile.bidang_pembedahan != 'PAEDIATRIC SURGERY'):
        messages.error(request, "You do not have permission to add this activity.")
        return redirect('paediatric_activities')

    current_year = datetime.now().year
    existing = SurgeryActivity.objects.filter(
        fraternity="Paediatric Surgery",
        year=current_year
    ).count()

    if existing == 0:
        period = "Jan-Jun"
    elif existing == 1:
        period = "Jul-Dec"
    else:
        messages.error(request, "The activities for this year are already complete.")
        return redirect('paediatric_activities')

    activity, created = SurgeryActivity.objects.get_or_create(
        fraternity="Paediatric Surgery",
        year=current_year,
        period=period,
        defaults={'status': 'not_started'}
    )
    activity.users.add(request.user)
    messages.success(request, f"Activity {period} {current_year} created successfully!")
    return redirect('paediatric_activities')

@login_required
def delete_paediatric_activity(request, activity_id):
    profile = getattr(request.user, 'profile', None)
    
    # Semak akses (hanya yang sah atau superuser boleh padam)
    if not request.user.is_superuser and (not profile or profile.bidang_pembedahan != 'PAEDIATRIC SURGERY'):
        messages.error(request, "You do not have permission to delete this activity.")
        return redirect('paediatric_activities')

    # Cari aktiviti dan padam
    activity = get_object_or_404(SurgeryActivity, id=activity_id)
    activity.delete()  # Ini akan turut memadam SurgeryActivityDetail secara automatik
    
    messages.success(request, "Activity has been successfully deleted/reset.")
    return redirect('paediatric_activities')

@login_required
def form_paediatric(request, activity_id):
    profile = getattr(request.user, 'profile', None)
    if not request.user.is_superuser and (not profile or profile.bidang_pembedahan != 'PAEDIATRIC SURGERY'):
        messages.error(request, "You do not have permission to access this form.")
        return redirect('paediatric_activities')

    activity = get_object_or_404(SurgeryActivity, id=activity_id)

    # 10 Parameter Terbaru dari Excel V2
    structure_domains = [
        "Development of awareness module on common neonatal surgical conditions requiring urgent referral, including biliary atresia.",
        "Issuance of a formal directive letter to Primary Care facilities regarding the standard counselling module for newborn jaundice and pale-stool awareness.",
        "Percentage of hospitals with paediatric surgical services implementing a National Standardised Biliary Atresia Work-up and Kasai Timing Algorithm.",
        "Number of hospitals with pediatric surgical services",
        "Percentage of Klinik Kesihatan (KK) providing on-site Liver Function Test (LFT) services for fractionated bilirubin measurement.",
        "Percentage of hospitals with paediatric surgical services equipped with access to a gazetted PICU or designated acute care beds for paediatric surgical patients.",
        "Total annual budget allocated for the purchase and maintenance of fractionated bilirubin machines and for community counselling materials related to prolonged jaundice and biliary atresia awareness.",
        "Total amount of budget allocated annually for long-term follow-up of biliary atresia patients and coordination of transplant costs with the national referral centre (HTA) and NTRC?",
        "Percentage of referrals for suspected biliary atresia documented with date of referral in the baby's health record (Buku Rekod Kesihatan Bayi & Kanak-kanak) or electronic medical system.",
        "Functional integration of the Biliary Atresia Registry into the National Surgical Anaesthesia Procedure Registry (NSAPR) Dashboard."
    ]
    process_domains = [
        "Percentage of infants with pale stool and hyperbilirubinemia referred to tertiary within 5 working days from blood taking.",
        "Percentage of suspected Biliary Atresia cases completing work-up ≤ 5 working days or by 60 days of life, whichever occurs first.",
        "Percentage of Kasai operation conducted within ten (10) working days after completed work-up or by 60 days of life, whichever occurs first.",
        "Compliance rate of Kasai operations with the Ministry of Health (MOH) Surgical Safety Sign-out List (SSSL)",
        "Compliance rate of postoperative Kasai patients with the Standardised National Post-Kasai Management Protocol.",
        "Rate of readmission for ascending cholangitis within 30 days of the Kasai procedure."
    ]
    outcome_domains = [
        "Percentage of Kasai operations performed at or before 60 days of life.",
        "Rate of jaundice clearance (Total Bilirubin < 34 µmol/L) at 6 months following the Kasai procedure.",
        "Incidence rate of Surgical Site Infection (SSI) in post-Kasai patients. Percentage of Kasai cases with surgical site infection (SSI)",
        "Total number of formal complaints related to the management of Biliary Atresia cases."
    ]

    details = SurgeryActivityDetail.objects.filter(activity=activity)
    detail_dict = {}
    for d in details:
        key = f"{d.category}_{d.domain}"
        detail_dict[key] = {
            "performances": d.performances_value,
            "denominator": d.denominator,
            "target": d.target,
            "weight": d.weight,
            "score": d.score,
            "wscore": d.weighted_score,
            "index": d.index
        }

    if request.method == "POST":
        SurgeryActivityDetail.objects.filter(activity=activity).delete()

        def save_category(category_name, domains):
            total = Decimal('0')
            for i, domain in enumerate(domains, start=1):
                performances = request.POST.get(f"{category_name}_performances_{i}", "0")
                denominator = request.POST.get(f"{category_name}_denominator_{i}", "0")
                target = request.POST.get(f"{category_name}_target_{i}", "0")
                weight = request.POST.get(f"{category_name}_weight_{i}", "0")
                
                try: num_d = Decimal(str(performances))
                except: num_d = Decimal('0')
                try: den_d = Decimal(str(denominator))
                except: den_d = Decimal('0')
                try: wgt_d = Decimal(str(weight))
                except: wgt_d = Decimal('0')
                
                if den_d > 0:
                    score_d = (num_d / den_d) * Decimal('100')
                    wscore_d = (num_d / den_d) * wgt_d
                    index_d = num_d / den_d
                else:
                    score_d = Decimal('0')
                    wscore_d = Decimal('0')
                    index_d = Decimal('0')
                    
                score_f = float(score_d.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
                wscore_f = float(wscore_d.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
                index_f = float(index_d.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))

                SurgeryActivityDetail.objects.create(
                    activity=activity,
                    category=category_name,
                    domain=domain,
                    performances_value=int(performances) if performances else 0,
                    denominator=int(denominator) if denominator else 0,
                    target=int(target) if target else 0,
                    weight=float(weight) if weight else 0,
                    score=score_f,
                    weighted_score=wscore_f,
                    index=index_f
                )
                total += Decimal(str(wscore_f))
            return float(total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))

        activity.total_structure = save_category("structure", structure_domains)
        activity.total_process = save_category("process", process_domains)
        activity.total_outcome = save_category("outcome", outcome_domains)
        activity.status = "completed"
        activity.save()

        messages.success(request, "Data has been successfully saved.")
        return redirect('paediatric_activities')

    return render(request, "accounts/form_paediatric.html", {
        "activity": activity,
        "structure_domains": structure_domains,
        "process_domains": process_domains,
        "outcome_domains": outcome_domains,
        "detail_dict": detail_dict,
    })

@login_required
def dashboard_paediatric(request):
    selected_year = int(request.GET.get('year', datetime.now().year))
    selected_period = request.GET.get('period', 'Jan-Jun')

    activities = SurgeryActivity.objects.filter(
        fraternity="Paediatric Surgery",
        status="done",
        year=selected_year,
        period=selected_period
    )

    if not activities.exists():
        context = {
            "selected_year": selected_year,
            "selected_period": selected_period,
            "years": list(range(2020, datetime.now().year + 2)),
            "total_structure_raw": 0,
            "total_process_raw": 0,
            "total_outcome_raw": 0,
            "total_structure": 0,
            "total_process": 0,
            "total_outcome": 0,
            "overall_index": 0,
            "domain_rows": [],
        }
        return render(request, "accounts/dashboard_paediatric.html", context)

    activity = activities.first()
    details = SurgeryActivityDetail.objects.filter(activity=activity)

    total_structure_raw = min(float(sum(details.filter(category="structure").values_list("weighted_score", flat=True)) or 0.0), 1.0)
    total_process_raw   = min(float(sum(details.filter(category="process").values_list("weighted_score", flat=True)) or 0.0), 1.0)
    total_outcome_raw   = min(float(sum(details.filter(category="outcome").values_list("weighted_score", flat=True)) or 0.0), 1.0)

    total_structure = total_structure_raw * 0.3
    total_process   = total_process_raw   * 0.4
    total_outcome   = total_outcome_raw   * 0.3
    overall_index   = min(total_structure + total_process + total_outcome, 1.0)

    domain_rows = [{
        "category": d.category.capitalize(),
        "domain": d.domain,
        "performances_value": d.performances_value,
        "target": d.target,
        "weight": d.weight,
        "score": d.score,
        "weighted_score": d.weighted_score,
        "index": d.index,
    } for d in details]

    context = {
        "total_structure_raw": round(total_structure_raw, 2),
        "total_process_raw":   round(total_process_raw, 2),
        "total_outcome_raw":   round(total_outcome_raw, 2),
        "total_structure":     round(total_structure, 2),
        "total_process":       round(total_process, 2),
        "total_outcome":       round(total_outcome, 2),
        "overall_index":       round(overall_index, 2),
        "domain_rows":         domain_rows,
        "years":               list(range(2020, datetime.now().year + 2)),
        "selected_year":       selected_year,
        "selected_period":     selected_period,
    }
    return render(request, "accounts/dashboard_paediatric.html", context)

@login_required
def cardiothoracic(request):
    return render(request, 'accounts/cardiothoracic.html')

@login_required
def obstetrics_gynaecology(request):
    return render(request, 'accounts/obstetrics_gynaecology.html')

@login_required
def otorhinolaryngology(request):
    return render(request, 'accounts/otorhinolaryngology.html')

@login_required
def plastic_reconstructive(request):
    return render(request, 'accounts/plastic_reconstructive.html')

@login_required
def oral_maxillofacial(request):
    return render(request, 'accounts/oral_maxillofacial.html')

@login_required
def public_health(request):
    return render(request, 'accounts/public_health.html')

@login_required
def family_medicine(request):
    return render(request, 'accounts/family_medicine.html')