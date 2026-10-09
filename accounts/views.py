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
    
    if not request.user.is_superuser and (not profile or profile.bidang_pembedahan != 'GENERAL SURGERY'):
        messages.error(request, "You do not have permission to access this form.")
        return redirect('general_surgery_activities')
    
    activity = get_object_or_404(SurgeryActivity, id=activity_id)

    # Parameter asal yang dikekalkan
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

                try: num_val = float(performances) if performances else 0.0
                except ValueError: num_val = 0.0
                try: den_val = float(denominator) if denominator else 0.0
                except ValueError: den_val = 0.0
                try: tgt_val = float(target) if target else 0.0
                except ValueError: tgt_val = 0.0

                calc_divisor = den_val if den_val > 0 else tgt_val
                score_f, wscore_f, index_f = calculate_domain_scores(num_val, calc_divisor, weight)

                SurgeryActivityDetail.objects.create(
                    activity=activity,
                    category=category_name,
                    domain=domain,
                    performances_value=num_val,
                    denominator=den_val,
                    target=tgt_val,
                    weight=float(weight) if weight else 0.0,
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

    total_structure_raw = min(float(sum(details.filter(category="structure").values_list("weighted_score", flat=True)) or 0.0), 1.0)
    total_process_raw = min(float(sum(details.filter(category="process").values_list("weighted_score", flat=True)) or 0.0), 1.0)
    total_outcome_raw = min(float(sum(details.filter(category="outcome").values_list("weighted_score", flat=True)) or 0.0), 1.0)

    # Pemberat General Surgery: 30% Structure, 40% Process, 30% Outcome
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
            "denominator": d.denominator,
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
    
    # Parameter Terbaharu dari Excel (CRC)
    structure_domains = [
        "Creation of a module for Awareness of Colorectal Cancer for public health sector personnels.",
        "Increase of Colorectal Cancer screening by 2% per year",
        "Renewal of Credentialing and Privileging every 2 years for MOH surgeons performing surgery in Colorectal Cancer",
        "Creation of a mobile Cancer Awareness Promotion Unit in each JKN",
        "Creation of a Colorectal Cancer Navigation (One stop centre) in each Klinik Kesihatan involved in Colorectal Cancer screening",
        "Creation of regional services for 3 Specialized Colorectal Services",
        "Percentage of state hospitals with complete set up of Colorectal Surgery Unit.",
        "Percentage of state hospitals with 2 NSR certified Colorectal Surgeons",
        "Colorectal Cancer Notification via MyHDW database."
    ]
    
    process_domains = [
        "Percentage of utilization of screening iFOBT kits",
        "Individual with positive screening iFOBT must undergo colonoscopy within 1 month.",
        "Adherence to Colorectal Cancer Surgery Prehabilitation Programme.",
        "Standardization of Colorectal Cancer Procedure Specific Consent Forms nationwide",
        "Adherence to Safe Surgery Saves Life ( SSSL ) guidelines",
        "Adherence to vPOMR reporting",
        "Adherence to Surgical Site Infection (SSI) reporting"
    ]
    
    outcome_domains = [
        "Referral for suspected Colorectal Cancer must be given appointment within 2 weeks of date of referral",
        "Unclear surgical margins in Rectal Cancer Surgery (Total Mesorectal Excision)",
        "Elective major colorectal cancer resection by laparoscopic surgery",
        "Peri-operative mortality rate for all elective major colorectal resection",
        "Rate of Surgical Site Infection after Major Elective Colorectal Cancer Resection",
        "Number of complaints via ‘SISTEM PENGURUSAN ADUAN AWAM (SISPAA) berasas’ per year"
    ]
    
    detail_dict = {}
    all_details = GSColorectalDetail.objects.filter(activity=activity)
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
        GSColorectalDetail.objects.filter(activity=activity).delete()
        
        def save_domain(category, domain_name, i):
            performances = request.POST.get(f'{category}_performances_{i}', '0')
            denominator = request.POST.get(f'{category}_denominator_{i}', '0')
            target = request.POST.get(f'{category}_target_{i}', '0')
            weight = request.POST.get(f'{category}_weight_{i}', '0')
            
            # Use float instead of int to prevent ValueError with decimal inputs like 0.01
            try: num_val = float(performances) if performances else 0.0
            except ValueError: num_val = 0.0
            
            try: den_val = float(denominator) if denominator else 0.0
            except ValueError: den_val = 0.0
            
            try: tgt_val = float(target) if target else 0.0
            except ValueError: tgt_val = 0.0

            calc_divisor = den_val if den_val > 0 else tgt_val
            score_f, wscore_f, index_f = calculate_domain_scores(num_val, calc_divisor, weight)
            
            try:
                EmergencyTraumaDetail.objects.create(
                    activity=activity,
                    category=category,
                    domain_name=domain_name,
                    performances_value=num_val,
                    denominator=den_val,
                    target=tgt_val,
                    weight=float(weight) if weight else 0.0,
                    score=score_f,
                    weighted_score=wscore_f,
                    index=index_f
                )
            except TypeError:
                 EmergencyTraumaDetail.objects.create(
                    activity=activity,
                    category=category,
                    domain_name=domain_name,
                    performances_value=num_val,
                    target=tgt_val,
                    weight=float(weight) if weight else 0.0,
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
        
        # Keseragaman Status
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
        activity = GSColorectalActivity.objects.get(year=selected_year, period=selected_period, status="completed")
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
    if not request.user.is_superuser and (not profile or profile.bidang_pembedahan != 'OPHTHALMOLOGY'):
        messages.error(request, "You do not have permission to access this form.")
        return redirect('ophthalmology_activities')
    
    activity = get_object_or_404(SurgeryActivity, id=activity_id)

    # Parameter sedia ada (Boleh ditukar jika anda ada senarai baharu kelak)
    structure_domains = [
        "KOSPEN cataract finder policy (Written policy ensuring all KOSPEN group members are trained as cataract finders)",
        "Vision screening for patients above 60 years at KK",
        "Referral of low vision patients to primary care optometrist",
        "MOH Cataract Management Pathway guideline",
        "Refraction room for optometrist at Level 1 KK",
        "Dedicated ultraclean ophthalmology operating theatre",
        "Klinik Katarak KKM mobile set availability",
        "RALoV Flip Chart availability",
        "Smart vision chart per clinic",
        "Slit lamp per clinic",
        "Refraction set and optometrist examination chair per clinic",
        "Fully equipped hospital facilities for optometrist",
        "Hospital with ophthalmologist or permanent cataract outreach",
        "KOSPEN centres with trained cataract finders and RALoV Chart",
        "Level 1 KK with optometrist per state",
        "Minimum optometrist staffing for ophthalmology clinics",
        "Budget for Annual Primary Eye Care Training",
        "National ToT for phaco trainers",
        "MySejahtera vision screening question",
        "Patient journey mapping for cataract"
    ]
    
    process_domains = [
        "Cataract patients referred to KK and seen",
        "Cataract patients referred to eye clinic and seen",
        "Cataract surgery waiting time",
        "Cancellation rate of elective cataract surgery",
        "SSSL practice audit",
        "POMR Reporting",
        "PCI practice audit compliance"
    ]
    
    outcome_domains = [
        "Cataract surgery performed under Daycare",
        "Cataract complication rate",
        "Post-operative refractive surprise rate",
        "Audit completion rate",
        "Rate of elective post-operative endophthalmitis",
        "Anaesthesia-related mortality rate",
        "Infectious endophthalmitis following cataract surgery",
        "BCVA better than 6/12 within 3 months post-surgery",
        "Visual acuity outcome in patients without co-morbidity",
        "IOL availability rate",
        "IOL availability for all cataract surgery patients",
        "Pathway to acquire IOL for Malaysian citizens"
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
        status="completed",
        year=selected_year,
        period=selected_period
    )

    if not activities.exists():
        context = {
            "selected_year": selected_year,
            "selected_period": selected_period,
            "years": list(range(2020, datetime.now().year + 2)),
            "total_structure_raw": 0, "total_process_raw": 0, "total_outcome_raw": 0,
            "total_structure": 0, "total_process": 0, "total_outcome": 0,
            "overall_index": 0, "domain_rows": []
        }
        return render(request, "accounts/dashboard_ophthalmology.html", context)

    activity = activities.first()
    details = SurgeryActivityDetail.objects.filter(activity=activity)

    total_structure_raw = min(float(sum(details.filter(category="structure").values_list("weighted_score", flat=True)) or 0.0), 1.0)
    total_process_raw = min(float(sum(details.filter(category="process").values_list("weighted_score", flat=True)) or 0.0), 1.0)
    total_outcome_raw = min(float(sum(details.filter(category="outcome").values_list("weighted_score", flat=True)) or 0.0), 1.0)

    # Pemberat Excel Ophthalmology: 0.5 (Structure), 0.3 (Process), 0.2 (Outcome)
    total_structure = total_structure_raw * 0.5
    total_process = total_process_raw * 0.3
    total_outcome = total_outcome_raw * 0.2
    overall_index = min(total_structure + total_process + total_outcome, 1.0)

    domain_rows = []
    for d in details:
        domain_rows.append({
            "category": d.category.capitalize(),
            "domain": d.domain,
            "performances_value": d.performances_value,
            "denominator": d.denominator,
            "target": d.target,
            "weight": d.weight,
            "score": d.score,
            "weighted_score": d.weighted_score,
            "index": d.index,
        })

    context = {
        "selected_year": selected_year, "selected_period": selected_period,
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
    
    # Parameter Diekstrak dari Excel NSAPR ETD Trauma Final
    structure_domains = [
        "National Trauma Policy / National Pre-Hospital Care Policy",
        "Trauma Resuscitation Bay / DCR Suite / Whole Body CT Scan / Dedicated Trauma Operation Theatre",
        "Essential / Advanced trauma resuscitation, diagnostic, surgical and anaesthetic equipment",
        "Emergency Physicians / Trained hospital health workers / Surgeons, Anaesthesiologists, Intensivists",
        "Specific emergency trauma care allocation",
        "Referral tracking and logs / Digital patient records / EHRs / Trauma registries"
    ]
    
    process_domains = [
        "Pre-Hospital Care - Scramble Time (Dispatched to En Route) - Less than 5 minutes",
        "Pre-Hospital Care - Response Time (Dispatched to At Scene) - Less than 15 minutes",
        "Pre-Hospital Care - Scene Time (Arrival to Transporting) - Less than 15 minutes",
        "Resuscitation - Trauma Pre-Alert Notification - Improve in-hospital preparation",
        "Resuscitation - Triage / Trauma Reception - Malaysian Triage Protocol, Bypass Policy",
        "Resuscitation - Resuscitation - Trauma Team Activation (TTA), Emergency O Blood, Massive Transfusion Protocol",
        "Post Resuscitation Care - Emergency Imaging - Portable X-ray Machine, Whole Body CT Scan",
        "Post Resuscitation Care - Stabilisation, Continuation of Care & Monitoring - Primary team interval assessment",
        "Emergency Interventions - Operation Theatre / Interventional Radiology - Disposition according to stability"
    ]
    
    outcome_domains = [
        "Access to Care - Stabilization of unstable patients and transfer to appropriate center / Optimal care",
        "Decision to Disposition - Within 1 hour",
        "Time to Disposition - Within 2 hours",
        "Mortality Review - Mortality review for all trauma cases, Improved mortality rate",
        "Equity - Reaches rural and underserved, Equitable care regardless of socioeconomic status"
    ]
    
    detail_dict = {}
    all_details = EmergencyTraumaDetail.objects.filter(activity=activity)
    for d in all_details:
        key = f"{d.category}_{d.domain_name}"
        detail_dict[key] = {
            'performances': d.performances_value,
            'denominator': getattr(d, 'denominator', 0), # in case denominator is not yet in this model
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
            # Fallback for models without denominator field yet
            denominator = request.POST.get(f'{category}_denominator_{i}', '0')
            target = request.POST.get(f'{category}_target_{i}', '0')
            weight = request.POST.get(f'{category}_weight_{i}', '0')
            
            # Using Denominator for calculation if present, else fallback to Target
            calc_divisor = denominator if float(denominator or 0) > 0 else target
            score_f, wscore_f, index_f = calculate_domain_scores(performances, calc_divisor, weight)
            
            # Use try-except in case EmergencyTraumaDetail model doesn't have 'denominator' column yet.
            # To ensure it doesn't crash, we'll try to insert denominator, otherwise skip it.
            try:
                EmergencyTraumaDetail.objects.create(
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
            except TypeError:
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

    # Pemberat ETD Trauma: 30% Structure, 60% Process, 10% Outcome
    total_structure = total_structure_raw * 0.3
    total_process = total_process_raw * 0.6
    total_outcome = total_outcome_raw * 0.1

    overall_saoi = min(total_structure + total_process + total_outcome, 1.0)

    domain_rows = []
    for d in details:
        domain_rows.append({
            'category': d.category.capitalize(),
            'domain': d.domain_name,
            'performances_value': d.performances_value,
            'denominator': getattr(d, 'denominator', 0),
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
    
    # Parameter Terbaharu dari Excel "NSAPR UGI Gastric Ca Final"
    structure_domains = [
        "National Strategic Plan for Gastric Cancer",
        "Awareness of Mark’s quadrant for gastric cancer screening",
        "Development Guidelines for Gastric Cancer",
        "Regular regional meetings with primary care HCPs under societies",
        "1. Fully equipped endoscopic suites in each UGi center / 2. Upgrading OR for advanced MIS & HIPEC / 3. Fully equipped laparoscopic OT / 4. Preoperative risk stratification assessment tool",
        "Adequate consumables in each upper gastrointestinal surgical center",
        "Data manager to maintain database gastric cancer in UGI centers",
        "Number of board-certified UGI surgeons",
        "Allocations specific to UGI unit in each center as fixed portion in a dedicated warrant.",
        "Digitalization (SP.6 / SH.6)"
    ]
    
    process_domains = [
        "Percentage of patients referred to Upper GI center within 2 weeks once MARK’s quadrant criteria are fulfilled.",
        "Percentage of patients undergoing diagnostic upper GI endoscopy within 14-calendar days from time of referral.",
        "Development of Nutrition Module",
        "Development of feeding tube care protocol",
        "Establishment of nutrition support team in UGI centers",
        "Regular multidisciplinary team meetings (MDT)",
        "Adherence to Surgical Safety Checklist (SSSL)",
        "Structured peri-operative gastrectomy anaesthesia and surgical protocol",
        "Referral rate for indicated cases (Mark's quadrant score >9)",
        "Provision of mortality rate in each UGI centers",
        "Provision of hygiene education",
        "Postoperative and wound care clinic service availability",
        "Compliance of Surgical Site Infection (SSI) audit"
    ]
    
    outcome_domains = [
        "National Gastric Cancer Awareness Month - October",
        "Fast-track access to endoscopic facilities by specialists.",
        "Time for definitive treatment after diagnosis confirmed within ONE calendar month at diagnosis in UGI center.",
        "Dedicated two-monthly mortality and morbidity discussions via virtual meetings with UGI trainees nationwide.",
        "Annual Peri-operative mortality review (POMR) Report",
        "Wound Care Clinics",
        "Annual national surgical site infection (SSI) Audit",
        "Patient Satisfaction Survey",
        "Two-yearly Patient Reported Outcome Measures (PROM) and Patient Reported Experience Measures (PREM) reports",
        "Outreach program in Peninsular and Borneo counterparts.",
        "Enable walk-in referrals to UGI centers."
    ]
    
    detail_dict = {}
    all_details = UpperGIDetail.objects.filter(activity=activity)
    for d in all_details:
        key = f"{d.category}_{d.domain_name}"
        detail_dict[key] = {
            'performances': d.performances_value,
            'denominator': getattr(d, 'denominator', 0), 
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
            denominator = request.POST.get(f'{category}_denominator_{i}', '0')
            target = request.POST.get(f'{category}_target_{i}', '0')
            weight = request.POST.get(f'{category}_weight_{i}', '0')
            
            try: num_val = float(performances) if performances else 0.0
            except ValueError: num_val = 0.0
            
            try: den_val = float(denominator) if denominator else 0.0
            except ValueError: den_val = 0.0
            
            try: tgt_val = float(target) if target else 0.0
            except ValueError: tgt_val = 0.0
            
            # Using Denominator for calculation if present, else fallback to Target
            calc_divisor = den_val if den_val > 0 else tgt_val
            score_f, wscore_f, index_f = calculate_domain_scores(num_val, calc_divisor, weight)

            try:
                UpperGIDetail.objects.create(
                    activity=activity,
                    category=category,
                    domain_name=domain_name,
                    performances_value=num_val,
                    denominator=den_val,
                    target=tgt_val,
                    weight=float(weight) if weight else 0.0,
                    score=score_f,
                    weighted_score=wscore_f,
                    index=index_f
                )
            except TypeError:
                UpperGIDetail.objects.create(
                    activity=activity,
                    category=category,
                    domain_name=domain_name,
                    performances_value=num_val,
                    target=tgt_val,
                    weight=float(weight) if weight else 0.0,
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
        activity = UpperGIActivity.objects.get(year=selected_year, period=selected_period, status="completed")
        
        details = UpperGIDetail.objects.filter(activity=activity)
        
        # Recalculate raw values to ensure accuracy
        total_structure_raw = min(float(sum(details.filter(category="structure").values_list("weighted_score", flat=True)) or 0.0), 1.0)
        total_process_raw = min(float(sum(details.filter(category="process").values_list("weighted_score", flat=True)) or 0.0), 1.0)
        total_outcome_raw = min(float(sum(details.filter(category="outcome").values_list("weighted_score", flat=True)) or 0.0), 1.0)

        # Apply Upper GI Weights: 30% Structure, 40% Process, 30% Outcome
        total_structure = total_structure_raw * 0.3
        total_process = total_process_raw * 0.4
        total_outcome = total_outcome_raw * 0.3
        overall_index = min(total_structure + total_process + total_outcome, 1.0)
        
        domain_rows = []
        for d in details:
            domain_rows.append({
                'category': d.category.capitalize(),
                'domain': d.domain_name,
                'performances_value': d.performances_value,
                'denominator': getattr(d, 'denominator', 0),
                'target': d.target,
                'weight': d.weight,
                'score': d.score,
                'weighted_score': d.weighted_score,
                'index': d.index
            })
    except UpperGIActivity.DoesNotExist:
        total_structure_raw = 0
        total_process_raw = 0
        total_outcome_raw = 0
        total_structure = 0
        total_process = 0
        total_outcome = 0
        overall_index = 0
        domain_rows = []
    
    years = UpperGIActivity.objects.values_list('year', flat=True).distinct().order_by('-year')
    if not years:
        years = [datetime.now().year, datetime.now().year + 1]
    
    return render(request, 'accounts/dashboard_upper_gi.html', {
        'total_structure_raw': total_structure_raw,
        'total_process_raw': total_process_raw,
        'total_outcome_raw': total_outcome_raw,
        'total_structure': total_structure,
        'total_process': total_process,
        'total_outcome': total_outcome,
        'overall_index': overall_index,
        'domain_rows': domain_rows,
        'years': years,
        'selected_year': selected_year,
        'selected_period': selected_period,
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
    
    if not request.user.is_superuser and (not profile or profile.bidang_pembedahan != 'GENERAL SURGERY BREAST AND ENDOCRINE'):
        messages.error(request, "You do not have permission to access this form.")
        return redirect('gsbreast_endocrine_activities')
    
    activity = get_object_or_404(SurgeryActivity, id=activity_id)

    # Parameter Terbaharu dari Excel B&E (Breast Ca) Final
    structure_domains = [
        "Breast Cancer Awareness Programme",
        "Patient Navigation Program (PNP) in all tertiary centres with breast and endocrine services",
        "Availability of a mobile screening unit for clinical breast assessment and imaging",
        "Development of regional Intra-operative radiotherapy (IORT) centres in all 14 states",
        "Availability of health promotion and education tools on breast cancer awareness in every Public Health Clinic",
        "Dual method Sentinel Lymph Node Biopsy (SLNB) service in all 14 tertiary hospitals",
        "Presence of trained health care promoters responsible for breast cancer awareness and activities",
        "Availability of breast care navigators (BCN) for patient support in all 14 tertiary hospitals",
        "Dedicated budget for Breast Cancer Awareness and Activities",
        "A well developed mobile apps for patient education and primary care appointment scheduling",
        "Implementation of hospital based breast cancer registry linked to the national cancer registry"
    ]
    
    process_domains = [
        "Outreach screening program",
        "Referral of new suspected malignancy cases is to be seen within 2 weeks in surgical clinic",
        "Percentage of new cases discussed in the MDT (Multidisciplinary Team) meeting",
        "Informed consent by the incharge specialists of treatment plans for all patients",
        "All surgeons involved in breast cancer management must obtain credentialing and privileging (C&P)",
        "Pre-operative anaesthetic assessment clinic for all elective cases",
        "Percentage of morbidity rate following elective breast surgeries",
        "Use of peri-operative prophylactic antibiotics in patients who have received neoadjuvant chemotherapy"
    ]
    
    outcome_domains = [
        "Screening Mammogram coverage for women aged 50-74",
        "Waiting time of first surgical clinic review within 2 weeks for new cases",
        "Clear margins post breast conserving surgery",
        "POMR Rate in elective cases",
        "The surgical site infection rate post breast conserving surgery or mastectomy without reconstruction",
        "The use of BREAST-Q questionnaire to assess patient satisfactory on cosmetic outcome",
        "Time to initiation of first treatment (either surgery or chemotherapy) following diagnosis within 6 weeks"
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

    # Parameter Lama yang Terperinci (Dikekalkan)
    structure_domains = [
        "Number of FTE consultant thoracic surgeons (Ensures sufficient specialist availability for managing chest and pulmonary surgical cases)",
        "Dedicated thoracic operating theatre (Provides a safe and appropriately equipped environment for thoracic procedures)",
        "Availability of VATS equipment — video-assisted thoracoscopic surgery (Enables minimally invasive chest surgery with improved patient recovery)",
        "Pulmonary function testing facilities (Supports pre-operative respiratory assessment to guide surgical decision-making)",
        "Thoracic ICU/HDU beds availability (Ensures adequate critical care capacity for post-thoracic surgery monitoring and recovery)"
    ]
    process_domains = [
        "MDT meetings for thoracic oncology (Ensures multidisciplinary review of lung and thoracic cancer cases before treatment)",
        "Pre-operative staging and imaging protocol compliance (Tracks completeness of radiological workup before thoracic surgery)",
        "Intraoperative bronchoscopy utilization (Measures use of airway visualization during thoracic procedures for safety and accuracy)",
        "Adherence to ERATS protocol — enhanced recovery after thoracic surgery (Tracks compliance with evidence-based recovery pathways to reduce length of stay)",
        "Post-operative chest physiotherapy protocol adherence (Ensures respiratory rehabilitation is delivered to reduce pulmonary complications)"
    ]
    outcome_domains = [
        "30-day surgical mortality rate (Rate of deaths within 30 days of thoracic surgical intervention)",
        "Rate of prolonged air leak greater than 7 days (Tracks a key post-operative complication following pulmonary resection)",
        "Post-operative pulmonary complication rate (Rate of respiratory adverse events such as pneumonia or atelectasis after thoracic surgery)",
        "Mean length of hospital stay (Average inpatient duration after thoracic surgery as an indicator of recovery efficiency)",
        "Readmission rate within 30 days (Proportion of patients requiring hospital readmission within 30 days of thoracic surgery)"
    ]

    details = SurgeryActivityDetail.objects.filter(activity=activity)
    detail_dict = {}
    for d in details:
        key = f"{d.category}_{d.domain}"
        detail_dict[key] = {
            "performances": d.performances_value,
            "denominator": d.denominator,  # Lajur denominator baharu
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
        status="done",  # <--- INI PERLU DITUKAR
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


# =============================================
# GENERAL SURGERY TRAUMA
# =============================================
@login_required
def gstrauma(request):
    return render(request, 'accounts/gstrauma.html')

@login_required
def gstrauma_activities(request):
    year = datetime.now().year
    activities = SurgeryActivity.objects.filter(
        fraternity="General Surgery Trauma",
        year=year
    ).annotate(
        period_order=Case(
            When(period='Jan-Jun', then=1),
            When(period='Jul-Dec', then=2),
            default=3,
            output_field=IntegerField()
        )
    ).order_by('period_order')

    return render(request, 'accounts/gstrauma_activities.html', {
        'activities': activities,
        'year': year,
    })

@login_required
def add_gstrauma_activity(request):
    profile = getattr(request.user, 'profile', None)
    
    if not request.user.is_superuser and (not profile or profile.bidang_pembedahan != 'EMERGENCY & TRAUMA'): # Kekalkan akses untuk profil asal Trauma
        messages.error(request, "You do not have permission to add this activity.")
        return redirect('gstrauma_activities')
    
    current_year = datetime.now().year
    existing = SurgeryActivity.objects.filter(
        fraternity="General Surgery Trauma",
        year=current_year
    ).count()

    if existing == 0:
        period = "Jan-Jun"
    elif existing == 1:
        period = "Jul-Dec"
    else:
        messages.error(request, "The activities for this year are already complete.")
        return redirect('gstrauma_activities')

    activity, created = SurgeryActivity.objects.get_or_create(
        fraternity="General Surgery Trauma",
        year=current_year,
        period=period,
        defaults={'status': 'not_started'}
    )
    activity.users.add(request.user)
    messages.success(request, f"Activity {period} {current_year} created successfully!")
    return redirect('gstrauma_activities')

@login_required
def form_gstrauma(request, activity_id):
    profile = getattr(request.user, 'profile', None)
    
    if not request.user.is_superuser and (not profile or profile.bidang_pembedahan != 'EMERGENCY & TRAUMA'):
        messages.error(request, "You do not have permission to access this form.")
        return redirect('gstrauma_activities')
    
    activity = get_object_or_404(SurgeryActivity, id=activity_id)
    
    structure_domains = [
        "Existence of National Abdominal Trauma CPG",
        "Establishment of National Abdominal Trauma CPG",
        "Lead Hospital: Full compliance with tertiary trauma centres standards",
        "Non-lead Hospital: Functional surgical services available",
        "Lead Hospital: Full compliance with tertiary trauma centres standards (Equipment)",
        "Non-lead Hospital: Minimum trauma resuscitation set",
        "Lead Hospital: 24/7 Surgery coverage (Trauma Surgeons/General Surgeons, Trauma Nurses, Trauma Registry Data Manager)",
        "Non-lead Hospital: Minimum one general surgeon per hospital",
        "Lead Hospital: Allocation for Specific Trauma Surgical Care",
        "Non-lead Hospital: Allocation for Specific Surgical care",
        "Trauma registry established"
    ]
    
    process_domains = [
        "<3-hour transfer for major trauma cases",
        "Lead Hospital: ≥90% of Trauma Team Activation (TTA) cases undergo multidisciplinary review",
        "Non-lead Hospital: <2-hour transfer for major trauma cases",
        "All Hospital: 100% adherence to pre-op checklist",
        "All surgery will require documentation of consent",
        "SSSL 100% compliance",
        "Percentage of burn patients undergoing procedures with documented ASA classification prior to anesthesia.", # Memandangkan ini wujud dalam gambar Excel GS Trauma anda
        "Quarterly audit implemented",
        "Quarterly SSI audit"
    ]
    
    outcome_domains = [
        "Lead Hospital: <60 min to OR for crash trauma laparotomy in ≥90% of cases",
        "Non-lead Hospital: <2-hour referral time to definitive care in ≥90% of cases",
        "<5% complication rate for Trauma Laparotomy",
        "≥90% of Trauma cases reported",
        "<10% SSI rate",
        "≥80% satisfaction"
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
        return redirect('gstrauma_activities')

    return render(request, "accounts/form_gstrauma.html", {
        "activity": activity,
        "structure_domains": structure_domains,
        "process_domains": process_domains,
        "outcome_domains": outcome_domains,
        "detail_dict": detail_dict,
    })

@login_required
def dashboard_gstrauma(request):
    selected_year = int(request.GET.get('year', datetime.now().year))
    selected_period = request.GET.get('period', 'Jan-Jun')

    activities = SurgeryActivity.objects.filter(
        fraternity="General Surgery Trauma",
        status="completed",
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
            'overall_index': 0,
            'domain_rows': []
        }
        return render(request, 'accounts/dashboard_gstrauma.html', context)

    activity = activities.first()
    details = SurgeryActivityDetail.objects.filter(activity=activity)

    total_structure_raw = min(float(sum(details.filter(category="structure").values_list("weighted_score", flat=True)) or 0.0), 1.0)
    total_process_raw = min(float(sum(details.filter(category="process").values_list("weighted_score", flat=True)) or 0.0), 1.0)
    total_outcome_raw = min(float(sum(details.filter(category="outcome").values_list("weighted_score", flat=True)) or 0.0), 1.0)

    # Pemberat GS Trauma: 30% Structure, 40% Process, 30% Outcome
    total_structure = total_structure_raw * 0.3
    total_process = total_process_raw * 0.4
    total_outcome = total_outcome_raw * 0.3

    overall_index = min(total_structure + total_process + total_outcome, 1.0)

    domain_rows = [{
        'category': d.category.capitalize(),
        'domain': d.domain,
        'performances_value': d.performances_value,
        'denominator': d.denominator,
        'target': d.target,
        'weight': d.weight,
        'score': d.score,
        'weighted_score': d.weighted_score,
        'index': d.index,
    } for d in details]

    return render(request, 'accounts/dashboard_gstrauma.html', {
        'total_structure_raw': round(total_structure_raw, 2),
        'total_process_raw': round(total_process_raw, 2),
        'total_outcome_raw': round(total_outcome_raw, 2),
        'total_structure': round(total_structure, 2),
        'total_process': round(total_process, 2),
        'total_outcome': round(total_outcome, 2),
        'overall_index': round(overall_index, 2),
        'domain_rows': domain_rows,
        'years': list(range(2020, datetime.now().year + 2)),
        'selected_year': selected_year,
        'selected_period': selected_period,
    })

# =============================================
# ORTHOPAEDIC
# =============================================
@login_required
def orthopaedic(request):
    return render(request, 'accounts/orthopaedic.html')

@login_required
def orthopaedic_activities(request):
    year = datetime.now().year
    activities = SurgeryActivity.objects.filter(
        fraternity="Orthopaedic",
        year=year
    ).annotate(
        period_order=Case(
            When(period='Jan-Jun', then=1),
            When(period='Jul-Dec', then=2),
            default=3,
            output_field=IntegerField()
        )
    ).order_by('period_order')
    
    return render(request, 'accounts/orthopaedic_activities.html', {
        'activities': activities,
        'year': year,
    })

@login_required
def add_orthopaedic_activity(request):
    profile = getattr(request.user, 'profile', None)
    if not request.user.is_superuser and (not profile or profile.bidang_pembedahan != 'ORTHOPAEDIC'):
        messages.error(request, "You do not have permission to add this activity.")
        return redirect('orthopaedic_activities')

    current_year = datetime.now().year
    existing = SurgeryActivity.objects.filter(
        fraternity="Orthopaedic",
        year=current_year
    ).count()

    if existing == 0:
        period = "Jan-Jun"
    elif existing == 1:
        period = "Jul-Dec"
    else:
        messages.error(request, "The activities for this year are already complete.")
        return redirect('orthopaedic_activities')

    activity, created = SurgeryActivity.objects.get_or_create(
        fraternity="Orthopaedic",
        year=current_year,
        period=period,
        defaults={'status': 'not_started'}
    )
    activity.users.add(request.user)
    messages.success(request, f"Activity {period} {current_year} created successfully!")
    return redirect('orthopaedic_activities')

@login_required
def form_orthopaedic(request, activity_id):
    profile = getattr(request.user, 'profile', None)
    if not request.user.is_superuser and (not profile or profile.bidang_pembedahan != 'ORTHOPAEDIC'):
        messages.error(request, "You do not have permission to access this form.")
        return redirect('orthopaedic_activities')

    activity = get_object_or_404(SurgeryActivity, id=activity_id)

    # Parameter dari Excel Orthopaedic (OA) Final
    structure_domains = [
        "Percentage of case suspected osteoporosis had BMD done in a year",
        "Percentage of health clinic with medical officer trained and credential in performing intra articular Hyaluronic injection",
        "% training of Medical officer on intrarticular hyaluronic injection",
        "Facilities (Unspecified)",
        "Equipment (Unspecified)",
        "Workforce (Unspecified)",
        "Budget/ Financial allocation (Unspecified)",
        "Digitalization (Unspecified)"
    ]
    
    process_domains = [
        "Preoperative – Screening & Referral (Unspecified)",
        "Preoperative – Preoperative Care (Unspecified)",
        "Preoperative – Communication & Consent (Unspecified)",
        "Intraoperative - Surgical Safety (Unspecified)",
        "Postoperative - POMR (Unspecified)",
        "Perioperative – Infection Prevention and Control (IPC) (Unspecified)"
    ]
    
    outcome_domains = [
        "Access to Care (Unspecified)",
        "Surgical Safety (Unspecified)",
        "POMR (Unspecified)",
        "Patient Satisfaction (Unspecified)",
        "Equity (Unspecified)"
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
        return redirect('orthopaedic_activities')

    return render(request, "accounts/form_orthopaedic.html", {
        "activity": activity,
        "structure_domains": structure_domains,
        "process_domains": process_domains,
        "outcome_domains": outcome_domains,
        "detail_dict": detail_dict,
    })

@login_required
def dashboard_orthopaedic(request):
    selected_year = int(request.GET.get('year', datetime.now().year))
    selected_period = request.GET.get('period', 'Jan-Jun')

    activities = SurgeryActivity.objects.filter(
        fraternity="Orthopaedic",
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
        return render(request, "accounts/dashboard_orthopaedic.html", context)

    activity = activities.first()
    details = SurgeryActivityDetail.objects.filter(activity=activity)

    total_structure_raw = min(float(sum(details.filter(category="structure").values_list("weighted_score", flat=True)) or 0.0), 1.0)
    total_process_raw = min(float(sum(details.filter(category="process").values_list("weighted_score", flat=True)) or 0.0), 1.0)
    total_outcome_raw = min(float(sum(details.filter(category="outcome").values_list("weighted_score", flat=True)) or 0.0), 1.0)

    # Pemberat Orthopaedic: 30% Structure, 40% Process, 30% Outcome
    total_structure = total_structure_raw * 0.3
    total_process = total_process_raw * 0.4
    total_outcome = total_outcome_raw * 0.3
    overall_index = min(total_structure + total_process + total_outcome, 1.0)

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
        "total_process_raw": round(total_process_raw, 2),
        "total_outcome_raw": round(total_outcome_raw, 2),
        "total_structure": round(total_structure, 2),
        "total_process": round(total_process, 2),
        "total_outcome": round(total_outcome, 2),
        "overall_index": round(overall_index, 2),
        "domain_rows": domain_rows,
        "years": list(range(2020, datetime.now().year + 2)),
        "selected_year": selected_year,
        "selected_period": selected_period,
    }
    return render(request, "accounts/dashboard_orthopaedic.html", context)

# =============================================
# NEUROSURGERY (NS TBI)
# =============================================
@login_required
def neurosurgery(request):
    return render(request, 'accounts/neurosurgery.html')

@login_required
def neurosurgery_activities(request):
    year = datetime.now().year
    activities = SurgeryActivity.objects.filter(
        fraternity="Neurosurgery",
        year=year
    ).annotate(
        period_order=Case(
            When(period='Jan-Jun', then=1),
            When(period='Jul-Dec', then=2),
            default=3,
            output_field=IntegerField()
        )
    ).order_by('period_order')
    
    return render(request, 'accounts/neurosurgery_activities.html', {
        'activities': activities,
        'year': year,
    })

@login_required
def add_neurosurgery_activity(request):
    profile = getattr(request.user, 'profile', None)
    if not request.user.is_superuser and (not profile or profile.bidang_pembedahan != 'NEUROSURGERY'):
        messages.error(request, "You do not have permission to add this activity.")
        return redirect('neurosurgery_activities')

    current_year = datetime.now().year
    existing = SurgeryActivity.objects.filter(
        fraternity="Neurosurgery",
        year=current_year
    ).count()

    if existing == 0:
        period = "Jan-Jun"
    elif existing == 1:
        period = "Jul-Dec"
    else:
        messages.error(request, "The activities for this year are already complete.")
        return redirect('neurosurgery_activities')

    activity, created = SurgeryActivity.objects.get_or_create(
        fraternity="Neurosurgery",
        year=current_year,
        period=period,
        defaults={'status': 'not_started'}
    )
    activity.users.add(request.user)
    messages.success(request, f"Activity {period} {current_year} created successfully!")
    return redirect('neurosurgery_activities')

@login_required
def form_neurosurgery(request, activity_id):
    profile = getattr(request.user, 'profile', None)
    if not request.user.is_superuser and (not profile or profile.bidang_pembedahan != 'NEUROSURGERY'):
        messages.error(request, "You do not have permission to access this form.")
        return redirect('neurosurgery_activities')

    activity = get_object_or_404(SurgeryActivity, id=activity_id)

    # Parameter dari Excel NS TBI Final
    structure_domains = [
        "Traumatic Brain Injury and Non-accidental brain injury awareness programme.",
        "CPG Early management of head injury in adults",
        "Credential and priviledging compliance rate- All medical officer and specialist should be credentialled and privileged",
        "Fully equipped Dedicated Surgical Theatres, Neuro ICU/HDW and ward Beds, CT and MRI in all regional and non regional medium center",
        "Neurosurgical Equipment, Intervention Consumables, Microscope, Head clamp, Retractor Systems, Implants, Bone bank. CSF Diversion procedure",
        "Workforce: Neurosurgeons, Medical Officers, Medical Officers Assistants, Trained Staff Nurses, Aneathetist, Intensivist",
        "National Neurosurgical Budget",
        "EMRs, surgical registries, POMR tracking systems"
    ]
    
    process_domains = [
        "Time of medical officer reviewing head injury patients from the time of referral in ED <30mins",
        "Time of Ctscan from admission to CT room <1hr in hemodynamically stable patients.",
        "Percentage of intraoperative emergency cancellation rate due to hemodynamically unstable patients or patient not adequately resuscitated",
        "Wrong or inadequate consent",
        "Safe Surgery Saves life compliance rate",
        "Adequate intra-operative sedation during surgical procedure",
        "POMR completed at designated time frame",
        "Post-craniotomy infection rate"
    ]
    
    outcome_domains = [
        "Reduce referrals delay",
        "Akses terhadap pembedahan kecederaan otak (akses Bellwether)",
        "Craniotomy for TBI managed in ICU/HDW",
        "no incidence of wrong side surgery",
        "POMR for severe TBI <43%",
        "SSI postcraniotomy for TBI <20%",
        "Postoperative appointments, medications, sick leave given",
        "Reduce GAP <RM1.5mil"
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
                
                try: num_val = float(performances) if performances else 0.0
                except ValueError: num_val = 0.0
                
                try: den_val = float(denominator) if denominator else 0.0
                except ValueError: den_val = 0.0
                
                try: tgt_val = float(target) if target else 0.0
                except ValueError: tgt_val = 0.0

                calc_divisor = den_val if den_val > 0 else tgt_val
                score_f, wscore_f, index_f = calculate_domain_scores(num_val, calc_divisor, weight)

                SurgeryActivityDetail.objects.create(
                    activity=activity,
                    category=category_name,
                    domain=domain,
                    performances_value=num_val,
                    denominator=den_val,
                    target=tgt_val,
                    weight=float(weight) if weight else 0.0,
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
        return redirect('neurosurgery_activities')

    return render(request, "accounts/form_neurosurgery.html", {
        "activity": activity,
        "structure_domains": structure_domains,
        "process_domains": process_domains,
        "outcome_domains": outcome_domains,
        "detail_dict": detail_dict,
    })

@login_required
def dashboard_neurosurgery(request):
    selected_year = int(request.GET.get('year', datetime.now().year))
    selected_period = request.GET.get('period', 'Jan-Jun')

    activities = SurgeryActivity.objects.filter(
        fraternity="Neurosurgery",
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
        return render(request, "accounts/dashboard_neurosurgery.html", context)

    activity = activities.first()
    details = SurgeryActivityDetail.objects.filter(activity=activity)

    total_structure_raw = min(float(sum(details.filter(category="structure").values_list("weighted_score", flat=True)) or 0.0), 1.0)
    total_process_raw = min(float(sum(details.filter(category="process").values_list("weighted_score", flat=True)) or 0.0), 1.0)
    total_outcome_raw = min(float(sum(details.filter(category="outcome").values_list("weighted_score", flat=True)) or 0.0), 1.0)

    # Pemberat Neurosurgery: 30% Structure, 40% Process, 30% Outcome
    total_structure = total_structure_raw * 0.3
    total_process = total_process_raw * 0.4
    total_outcome = total_outcome_raw * 0.3
    overall_index = min(total_structure + total_process + total_outcome, 1.0)

    domain_rows = [{
        "category": d.category.capitalize(),
        "domain": d.domain,
        "performances_value": d.performances_value,
        "denominator": d.denominator,
        "target": d.target,
        "weight": d.weight,
        "score": d.score,
        "weighted_score": d.weighted_score,
        "index": d.index,
    } for d in details]

    context = {
        "total_structure_raw": round(total_structure_raw, 2),
        "total_process_raw": round(total_process_raw, 2),
        "total_outcome_raw": round(total_outcome_raw, 2),
        "total_structure": round(total_structure, 2),
        "total_process": round(total_process, 2),
        "total_outcome": round(total_outcome, 2),
        "overall_index": round(overall_index, 2),
        "domain_rows": domain_rows,
        "years": list(range(2020, datetime.now().year + 2)),
        "selected_year": selected_year,
        "selected_period": selected_period,
    }
    return render(request, "accounts/dashboard_neurosurgery.html", context)

# =============================================
# UROLOGY
# =============================================
@login_required
def urology(request):
    return render(request, 'accounts/urology.html')

@login_required
def urology_activities(request):
    year = datetime.now().year
    activities = SurgeryActivity.objects.filter(
        fraternity="Urology",
        year=year
    ).annotate(
        period_order=Case(
            When(period='Jan-Jun', then=1),
            When(period='Jul-Dec', then=2),
            default=3,
            output_field=IntegerField()
        )
    ).order_by('period_order')
    
    return render(request, 'accounts/urology_activities.html', {
        'activities': activities,
        'year': year,
    })

@login_required
def add_urology_activity(request):
    profile = getattr(request.user, 'profile', None)
    if not request.user.is_superuser and (not profile or profile.bidang_pembedahan != 'UROLOGY'):
        messages.error(request, "You do not have permission to add this activity.")
        return redirect('urology_activities')

    current_year = datetime.now().year
    existing = SurgeryActivity.objects.filter(
        fraternity="Urology",
        year=current_year
    ).count()

    if existing == 0:
        period = "Jan-Jun"
    elif existing == 1:
        period = "Jul-Dec"
    else:
        messages.error(request, "The activities for this year are already complete.")
        return redirect('urology_activities')

    activity, created = SurgeryActivity.objects.get_or_create(
        fraternity="Urology",
        year=current_year,
        period=period,
        defaults={'status': 'not_started'}
    )
    activity.users.add(request.user)
    messages.success(request, f"Activity {period} {current_year} created successfully!")
    return redirect('urology_activities')

@login_required
def form_urology(request, activity_id):
    profile = getattr(request.user, 'profile', None)
    if not request.user.is_superuser and (not profile or profile.bidang_pembedahan != 'UROLOGY'):
        messages.error(request, "You do not have permission to access this form.")
        return redirect('urology_activities')

    activity = get_object_or_404(SurgeryActivity, id=activity_id)

    # Parameter Diekstrak dari Gambar Excel Urologi
    structure_domains = [
        "100% HCP (doctors & MAs) involved in urolithiasis procedural management have undergone credentialing",
        "90% availability of Urology ward, fully equipped endourology",
        "80% of targeted population receiving educational material",
        "70% of primary care/district hospitals have basic equipment and diagnostics",
        "Availability of 3 urologist per tertiary care centre."
    ]
    
    process_domains = [
        "Rate of early presentation/consultation",
        "95% of patients with urolithiasis undergo definitive procedure within 6 weeks",
        "90% of patients presenting with recurrent stones offered metabolic workup",
        "100% of patients undergoing invasive procedures have documented informed consent",
        "All perioperative deaths following urolithiasis procedure audited (POMR)"
    ]
    
    outcome_domains = [
        "90% of patients receiving definitive urolithiasis procedure (Access to Care)",
        "Less than 5% unplanned re-admission or re-intervention rate (Surgical Safety)",
        "Less than 1% mortality rate attributed directly to surgical intervention (POMR)",
        "50% of general population can correctly identify key prevention strategies",
        "Average patient-reported satisfaction score of at least 80%"
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
        return redirect('urology_activities')

    return render(request, "accounts/form_urology.html", {
        "activity": activity,
        "structure_domains": structure_domains,
        "process_domains": process_domains,
        "outcome_domains": outcome_domains,
        "detail_dict": detail_dict,
    })

@login_required
def dashboard_urology(request):
    selected_year = int(request.GET.get('year', datetime.now().year))
    selected_period = request.GET.get('period', 'Jan-Jun')

    activities = SurgeryActivity.objects.filter(
        fraternity="Urology",
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
        return render(request, "accounts/dashboard_urology.html", context)

    activity = activities.first()
    details = SurgeryActivityDetail.objects.filter(activity=activity)

    total_structure_raw = min(float(sum(details.filter(category="structure").values_list("weighted_score", flat=True)) or 0.0), 1.0)
    total_process_raw = min(float(sum(details.filter(category="process").values_list("weighted_score", flat=True)) or 0.0), 1.0)
    total_outcome_raw = min(float(sum(details.filter(category="outcome").values_list("weighted_score", flat=True)) or 0.0), 1.0)

    # Pemberat Urology: 30% Structure, 40% Process, 30% Outcome
    total_structure = total_structure_raw * 0.3
    total_process = total_process_raw * 0.4
    total_outcome = total_outcome_raw * 0.3
    overall_index = min(total_structure + total_process + total_outcome, 1.0)

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
        "total_process_raw": round(total_process_raw, 2),
        "total_outcome_raw": round(total_outcome_raw, 2),
        "total_structure": round(total_structure, 2),
        "total_process": round(total_process, 2),
        "total_outcome": round(total_outcome, 2),
        "overall_index": round(overall_index, 2),
        "domain_rows": domain_rows,
        "years": list(range(2020, datetime.now().year + 2)),
        "selected_year": selected_year,
        "selected_period": selected_period,
    }
    return render(request, "accounts/dashboard_urology.html", context)

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

# =============================================
# CARDIOTHORACIC SURGERY (CTC - CABG)
# =============================================
@login_required
def cardiothoracic(request):
    return render(request, 'accounts/cardiothoracic.html')

@login_required
def cardiothoracic_activities(request):
    year = datetime.now().year
    activities = SurgeryActivity.objects.filter(
        fraternity="Cardiothoracic Surgery",
        year=year
    ).annotate(
        period_order=Case(
            When(period='Jan-Jun', then=1),
            When(period='Jul-Dec', then=2),
            default=3,
            output_field=IntegerField()
        )
    ).order_by('period_order')
    return render(request, 'accounts/cardiothoracic_activities.html', {
        'activities': activities,
        'year': year,
    })

@login_required
def add_cardiothoracic_activity(request):
    profile = getattr(request.user, 'profile', None)
    if not request.user.is_superuser and (not profile or profile.bidang_pembedahan != 'CARDIOTHORACIC SURGERY'):
        messages.error(request, "You do not have permission to add this activity.")
        return redirect('cardiothoracic_activities')

    current_year = datetime.now().year
    existing = SurgeryActivity.objects.filter(
        fraternity="Cardiothoracic Surgery",
        year=current_year
    ).count()

    if existing == 0:
        period = "Jan-Jun"
    elif existing == 1:
        period = "Jul-Dec"
    else:
        messages.error(request, "The activities for this year are already complete.")
        return redirect('cardiothoracic_activities')

    activity, created = SurgeryActivity.objects.get_or_create(
        fraternity="Cardiothoracic Surgery",
        year=current_year,
        period=period,
        defaults={'status': 'not_started'}
    )
    activity.users.add(request.user)
    messages.success(request, f"Activity {period} {current_year} created successfully!")
    return redirect('cardiothoracic_activities')

@login_required
def form_cardiothoracic(request, activity_id):
    profile = getattr(request.user, 'profile', None)
    if not request.user.is_superuser and (not profile or profile.bidang_pembedahan != 'CARDIOTHORACIC SURGERY'):
        messages.error(request, "You do not have permission to access this form.")
        return redirect('cardiothoracic_activities')

    activity = get_object_or_404(SurgeryActivity, id=activity_id)

    # Parameter dari Excel CTC (CABG)
    structure_domains = [
        "National Cardiothoracic Surgery Policy",
        "Fully equipped Cardiothoracic Surgical Centers according to National Policy and International Standards.",
        "Latest, specialised and functional equipments(Flow meter / IABP / ECMO / LVAD) in all MOH Cardiothoracic Surgical centers (according to international standards)",
        "Adequate number of surgeon/ man power in all Cardiothoracic Centers. ( according to National Policy and International Standard) One surgeon for 170 000 population",
        "RM 150 000 perCABG should be allocated",
        "CTC facilities with integrated medical system"
    ]
    process_domains = [
        "All cases for CABG should be referred within 3 months.",
        "No cancellation cases for CABG due to uncontrolled diabetes",
        "Refusal of CABG after consultation in Cardiothoracic Center should be less than 1%",
        "According to SSSL protocol",
        "All-cause death before discharge from the hospital or within 30 days of the procedure.",
        "A surgical site infection (SSI) is an infection occurring in the part of the body where surgery took place, typically within 30 days after the procedure. Caused by bacteria entering incisions, symptoms include redness, swelling, pain, warmth, and fever. Treatment involves antibiotics and, often, wound drainage."
    ]
    outcome_domains = [
        "Access to CABG in MOH facilities",
        "POMR should be < 4% in high volume center, and < 7% in low volume center..",
        "Return of questionnaire should be more than 90%",
        "Patients will go back to normal life after CABG"
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
        return redirect('cardiothoracic_activities')

    return render(request, "accounts/form_cardiothoracic.html", {
        "activity": activity,
        "structure_domains": structure_domains,
        "process_domains": process_domains,
        "outcome_domains": outcome_domains,
        "detail_dict": detail_dict,
    })

@login_required
def dashboard_cardiothoracic(request):
    selected_year = int(request.GET.get('year', datetime.now().year))
    selected_period = request.GET.get('period', 'Jan-Jun')

    activities = SurgeryActivity.objects.filter(
        fraternity="Cardiothoracic Surgery",
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
        return render(request, "accounts/dashboard_cardiothoracic.html", context)

    activity = activities.first()
    details = SurgeryActivityDetail.objects.filter(activity=activity)

    total_structure_raw = min(float(sum(details.filter(category="structure").values_list("weighted_score", flat=True)) or 0.0), 1.0)
    total_process_raw = min(float(sum(details.filter(category="process").values_list("weighted_score", flat=True)) or 0.0), 1.0)
    total_outcome_raw = min(float(sum(details.filter(category="outcome").values_list("weighted_score", flat=True)) or 0.0), 1.0)

    # Pemberat Excel Cardiothoracic: 0.5, 0.3, 0.2
    total_structure = total_structure_raw * 0.5
    total_process = total_process_raw * 0.3
    total_outcome = total_outcome_raw * 0.2
    overall_index = min(total_structure + total_process + total_outcome, 1.0)

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
        "total_process_raw": round(total_process_raw, 2),
        "total_outcome_raw": round(total_outcome_raw, 2),
        "total_structure": round(total_structure, 2),
        "total_process": round(total_process, 2),
        "total_outcome": round(total_outcome, 2),
        "overall_index": round(overall_index, 2),
        "domain_rows": domain_rows,
        "years": list(range(2020, datetime.now().year + 2)),
        "selected_year": selected_year,
        "selected_period": selected_period,
    }
    return render(request, "accounts/dashboard_cardiothoracic.html", context)

# =============================================
# OBSTETRICS & GYNAECOLOGY (O&G Cx Ca)
# =============================================
@login_required
def obstetrics_gynaecology(request):
    return render(request, 'accounts/obstetrics_gynaecology.html')

@login_required
def obstetrics_gynaecology_activities(request):
    year = datetime.now().year
    activities = SurgeryActivity.objects.filter(
        fraternity="Obstetrics & Gynaecology",
        year=year
    ).annotate(
        period_order=Case(
            When(period='Jan-Jun', then=1),
            When(period='Jul-Dec', then=2),
            default=3,
            output_field=IntegerField()
        )
    ).order_by('period_order')
    
    return render(request, 'accounts/obstetrics_gynaecology_activities.html', {
        'activities': activities,
        'year': year,
    })

@login_required
def add_obstetrics_gynaecology_activity(request):
    profile = getattr(request.user, 'profile', None)
    if not request.user.is_superuser and (not profile or profile.bidang_pembedahan != 'OBSTETRICS & GYNAECOLOGY'):
        messages.error(request, "You do not have permission to add this activity.")
        return redirect('obstetrics_gynaecology_activities')

    current_year = datetime.now().year
    existing = SurgeryActivity.objects.filter(
        fraternity="Obstetrics & Gynaecology",
        year=current_year
    ).count()

    if existing == 0:
        period = "Jan-Jun"
    elif existing == 1:
        period = "Jul-Dec"
    else:
        messages.error(request, "The activities for this year are already complete.")
        return redirect('obstetrics_gynaecology_activities')

    activity, created = SurgeryActivity.objects.get_or_create(
        fraternity="Obstetrics & Gynaecology",
        year=current_year,
        period=period,
        defaults={'status': 'not_started'}
    )
    activity.users.add(request.user)
    messages.success(request, f"Activity {period} {current_year} created successfully!")
    return redirect('obstetrics_gynaecology_activities')

@login_required
def form_obstetrics_gynaecology(request, activity_id):
    profile = getattr(request.user, 'profile', None)
    if not request.user.is_superuser and (not profile or profile.bidang_pembedahan != 'OBSTETRICS & GYNAECOLOGY'):
        messages.error(request, "You do not have permission to access this form.")
        return redirect('obstetrics_gynaecology_activities')

    activity = get_object_or_404(SurgeryActivity, id=activity_id)

    # Parameter Diekstrak dari Excel O&G Cx Ca Final
    structure_domains = [
        "Governance & Policy: Availability of Public Awareness and Education Modules / Implementation of National Immunisation & Screening Protocols / Active Cancer Registry (NCR) Reporting Structure",
        "Facilities: Multi-Agency Outreach Collaboration Readiness / Availability of Cervical Cancer Screening Kits (HPV & Pap Smear) / Tertiary Diagnostic and Therapeutic Capacity Readiness",
        "Equipment: Availability of Community Outreach & Self-Sampling Kits / Screening Consumables (HPV & Pap Smear) / Colposcopy and Gynae-Oncology Surgical Sets",
        "Workforce: Multi-agency and Multi-disciplinary Community Workforce Engagement / Competency and Training of Primary Care Workforce / Availability of Multi-Disciplinary Team (MDT)",
        "Budget/Financial: Availability of Dedicated Funding for Community HPV Vaccination and Screening / Financial Allocation for Outsourced Screening and Primary Care Services / Tertiary HPV Testing and Laboratory Services",
        "Digitalization: Integration of Cervical Cancer Services into Mobile Data Platforms / Digital Tracking and Defaulter Tracing System in Primary Care / Comprehensive Hospital Clinical Data Systems and Cancer Registry Reporting"
    ]
    
    process_domains = [
        "Preoperative - Screening & Referral: Community-level identification and referral of high-risk populations / Initial Screening, Diagnosis, and Referral Access / Timely Specialist Appointment for Malignancy Assessment",
        "Preoperative - Preoperative Care: Preoperative Care Applicability in Community Settings / Optimization of Preoperative Care and Timely Malignancy Operation",
        "Preoperative - Communication & Consent: Community-level Discussion on Screening Results / Discussion on Screening Results and Next Steps / Specialist-led Shared Decision-Making and Informed Consent",
        "Intraoperative - Surgical Safety: Intraoperative Surgical Safety Applicability in Community Settings / Primary Care / Full Adherence to Surgical Safety Protocols in Cervical Cancer Surgery",
        "Intraoperative - Anaesthesia Safety: Applicability of Intraoperative Anesthesia Safety in Community Settings / Primary Care / Adherence to Anesthesia Safety Standards and High-Dependency Care",
        "Postoperative - POMR: Community-level Support for Survivorship and Palliative Care / Shared Care Follow-up and Defaulter Tracing / Specialized Clinical Follow-up and Complication Management",
        "Perioperative - Infection Prevention and Control (IPC): Community-level Data Reporting and Public Awareness Review / Primary Care Performance Review and KPI Monitoring / Hospital-Level Clinical Audit and Outcome Monitoring"
    ]
    
    outcome_domains = [
        "Access to Care: Achievement of High Community Awareness on Cervical Cancer Prevention / National Cervical Cancer Screening Coverage Target / Timely Tertiary Treatment Initiation",
        "Surgical Safety: Minimal Community-Level Adverse Events and Effective Support / Achievement of Surgical Safety and Survival Standards",
        "POMR (General)",
        "Surgical Site Infection (General)",
        "Patient Satisfaction: Achievement of High Patient Satisfaction and Support Accessibility / Effective Communication of Screening Results and Patient Empowerment / Achievement of Specialist-Led Shared Decision-Making",
        "Equity: Achievement of Community Data Integrity and Surveillance Quality / Timely and Accurate Primary Care Reporting / Comprehensive Clinical Registry Compliance and Audit Closing"
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
                
                try: num_val = float(performances) if performances else 0.0
                except ValueError: num_val = 0.0
                
                try: den_val = float(denominator) if denominator else 0.0
                except ValueError: den_val = 0.0
                
                try: tgt_val = float(target) if target else 0.0
                except ValueError: tgt_val = 0.0

                calc_divisor = den_val if den_val > 0 else tgt_val
                score_f, wscore_f, index_f = calculate_domain_scores(num_val, calc_divisor, weight)

                SurgeryActivityDetail.objects.create(
                    activity=activity,
                    category=category_name,
                    domain=domain,
                    performances_value=num_val,
                    denominator=den_val,
                    target=tgt_val,
                    weight=float(weight) if weight else 0.0,
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
        return redirect('obstetrics_gynaecology_activities')

    return render(request, "accounts/form_obstetrics_gynaecology.html", {
        "activity": activity,
        "structure_domains": structure_domains,
        "process_domains": process_domains,
        "outcome_domains": outcome_domains,
        "detail_dict": detail_dict,
    })

@login_required
def dashboard_obstetrics_gynaecology(request):
    selected_year = int(request.GET.get('year', datetime.now().year))
    selected_period = request.GET.get('period', 'Jan-Jun')

    activities = SurgeryActivity.objects.filter(
        fraternity="Obstetrics & Gynaecology",
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
        return render(request, "accounts/dashboard_obstetrics_gynaecology.html", context)

    activity = activities.first()
    details = SurgeryActivityDetail.objects.filter(activity=activity)

    total_structure_raw = min(float(sum(details.filter(category="structure").values_list("weighted_score", flat=True)) or 0.0), 1.0)
    total_process_raw = min(float(sum(details.filter(category="process").values_list("weighted_score", flat=True)) or 0.0), 1.0)
    total_outcome_raw = min(float(sum(details.filter(category="outcome").values_list("weighted_score", flat=True)) or 0.0), 1.0)

    # Pemberat O&G Cx Ca: 50% Structure, 25% Process, 25% Outcome
    total_structure = total_structure_raw * 0.50
    total_process = total_process_raw * 0.25
    total_outcome = total_outcome_raw * 0.25
    overall_index = min(total_structure + total_process + total_outcome, 1.0)

    domain_rows = [{
        "category": d.category.capitalize(),
        "domain": d.domain,
        "performances_value": d.performances_value,
        "denominator": d.denominator,
        "target": d.target,
        "weight": d.weight,
        "score": d.score,
        "weighted_score": d.weighted_score,
        "index": d.index,
    } for d in details]

    context = {
        "total_structure_raw": round(total_structure_raw, 2),
        "total_process_raw": round(total_process_raw, 2),
        "total_outcome_raw": round(total_outcome_raw, 2),
        "total_structure": round(total_structure, 2),
        "total_process": round(total_process, 2),
        "total_outcome": round(total_outcome, 2),
        "overall_index": round(overall_index, 2),
        "domain_rows": domain_rows,
        "years": list(range(2020, datetime.now().year + 2)),
        "selected_year": selected_year,
        "selected_period": selected_period,
    }
    return render(request, "accounts/dashboard_obstetrics_gynaecology.html", context)

# =============================================
# OTORHINOLARYNGOLOGY (ENT NPC)
# =============================================
@login_required
def otorhinolaryngology(request):
    return render(request, 'accounts/otorhinolaryngology.html')

@login_required
def otorhinolaryngology_activities(request):
    year = datetime.now().year
    activities = SurgeryActivity.objects.filter(
        fraternity="Otorhinolaryngology",
        year=year
    ).annotate(
        period_order=Case(
            When(period='Jan-Jun', then=1),
            When(period='Jul-Dec', then=2),
            default=3,
            output_field=IntegerField()
        )
    ).order_by('period_order')
    
    return render(request, 'accounts/otorhinolaryngology_activities.html', {
        'activities': activities,
        'year': year,
    })

@login_required
def add_otorhinolaryngology_activity(request):
    profile = getattr(request.user, 'profile', None)
    if not request.user.is_superuser and (not profile or profile.bidang_pembedahan != 'OTORHINOLARYNGOLOGY'):
        messages.error(request, "You do not have permission to add this activity.")
        return redirect('otorhinolaryngology_activities')

    current_year = datetime.now().year
    existing = SurgeryActivity.objects.filter(
        fraternity="Otorhinolaryngology",
        year=current_year
    ).count()

    if existing == 0:
        period = "Jan-Jun"
    elif existing == 1:
        period = "Jul-Dec"
    else:
        messages.error(request, "The activities for this year are already complete.")
        return redirect('otorhinolaryngology_activities')

    activity, created = SurgeryActivity.objects.get_or_create(
        fraternity="Otorhinolaryngology",
        year=current_year,
        period=period,
        defaults={'status': 'not_started'}
    )
    activity.users.add(request.user)
    messages.success(request, f"Activity {period} {current_year} created successfully!")
    return redirect('otorhinolaryngology_activities')

@login_required
def form_otorhinolaryngology(request, activity_id):
    profile = getattr(request.user, 'profile', None)
    if not request.user.is_superuser and (not profile or profile.bidang_pembedahan != 'OTORHINOLARYNGOLOGY'):
        messages.error(request, "You do not have permission to access this form.")
        return redirect('otorhinolaryngology_activities')

    activity = get_object_or_404(SurgeryActivity, id=activity_id)

    # Parameter Diekstrak dari Excel ENT NPC Final
    structure_domains = [
        "NPC is included in National Strategic Plan for Cancer Control Programme (Revise version 2026-2030) (SC.1/SP.1/SH.1)",
        "NPC is included in awareness program at community level (SC.2/SP.2)",
        "Availability of in-house pathologist in tertiary hospital with ORL surgeon",
        "Availability of complete equipment for diagnostic and therapeutic purposes",
        "Number of Head & Neck surgeon in each zone (Northern, Southern, Eastern, Central, Sabah and Sarawak)",
        "Screening & Education budget for nasopharyngeal cancer (SC.5/SP.5)",
        "Equipment, Training & Education budget for nasopharyngeal cancer",
        "Data entry/tracking system via Head & Neck Cancer Registry"
    ]
    
    process_domains = [
        "Direct referral of all suspected NPC",
        "Multi-disciplinary team meeting for all NPC cases",
        "Preoperative Care (General)",
        "Complete consent given by patient / relatives",
        "Intraoperative - Surgical Safety (General)",
        "Intraoperative - Anaesthesia Safety (General)",
        "Postoperative - POMR (General)",
        "Perioperative - Infection Prevention and Control (IPC) (General)"
    ]
    
    outcome_domains = [
        "Percentage of NPC patients receiving an oncology appointment within 6 weeks of histological diagnosis.",
        "Rate of successful preservation of the internal carotid artery (ICA) during nasopharyngectomy",
        "POMR (General)",
        "Surgical Site Infection (General)",
        "Patient's satisfaction in NPC management",
        "Equity (General)"
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
                
                try: num_val = float(performances) if performances else 0.0
                except ValueError: num_val = 0.0
                
                try: den_val = float(denominator) if denominator else 0.0
                except ValueError: den_val = 0.0
                
                try: tgt_val = float(target) if target else 0.0
                except ValueError: tgt_val = 0.0

                calc_divisor = den_val if den_val > 0 else tgt_val
                score_f, wscore_f, index_f = calculate_domain_scores(num_val, calc_divisor, weight)

                SurgeryActivityDetail.objects.create(
                    activity=activity,
                    category=category_name,
                    domain=domain,
                    performances_value=num_val,
                    denominator=den_val,
                    target=tgt_val,
                    weight=float(weight) if weight else 0.0,
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
        return redirect('otorhinolaryngology_activities')

    return render(request, "accounts/form_otorhinolaryngology.html", {
        "activity": activity,
        "structure_domains": structure_domains,
        "process_domains": process_domains,
        "outcome_domains": outcome_domains,
        "detail_dict": detail_dict,
    })

@login_required
def dashboard_otorhinolaryngology(request):
    selected_year = int(request.GET.get('year', datetime.now().year))
    selected_period = request.GET.get('period', 'Jan-Jun')

    activities = SurgeryActivity.objects.filter(
        fraternity="Otorhinolaryngology",
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
        return render(request, "accounts/dashboard_otorhinolaryngology.html", context)

    activity = activities.first()
    details = SurgeryActivityDetail.objects.filter(activity=activity)

    total_structure_raw = min(float(sum(details.filter(category="structure").values_list("weighted_score", flat=True)) or 0.0), 1.0)
    total_process_raw = min(float(sum(details.filter(category="process").values_list("weighted_score", flat=True)) or 0.0), 1.0)
    total_outcome_raw = min(float(sum(details.filter(category="outcome").values_list("weighted_score", flat=True)) or 0.0), 1.0)

    # Pemberat ENT NPC: 40% Structure, 30% Process, 30% Outcome
    total_structure = total_structure_raw * 0.4
    total_process = total_process_raw * 0.3
    total_outcome = total_outcome_raw * 0.3
    overall_index = min(total_structure + total_process + total_outcome, 1.0)

    domain_rows = [{
        "category": d.category.capitalize(),
        "domain": d.domain,
        "performances_value": d.performances_value,
        "denominator": d.denominator,
        "target": d.target,
        "weight": d.weight,
        "score": d.score,
        "weighted_score": d.weighted_score,
        "index": d.index,
    } for d in details]

    context = {
        "total_structure_raw": round(total_structure_raw, 2),
        "total_process_raw": round(total_process_raw, 2),
        "total_outcome_raw": round(total_outcome_raw, 2),
        "total_structure": round(total_structure, 2),
        "total_process": round(total_process, 2),
        "total_outcome": round(total_outcome, 2),
        "overall_index": round(overall_index, 2),
        "domain_rows": domain_rows,
        "years": list(range(2020, datetime.now().year + 2)),
        "selected_year": selected_year,
        "selected_period": selected_period,
    }
    return render(request, "accounts/dashboard_otorhinolaryngology.html", context)

# =============================================
# PLASTIC & RECONSTRUCTIVE SURGERY
# =============================================
@login_required
def plastic_reconstructive(request):
    return render(request, 'accounts/plastic_reconstructive.html')

@login_required
def plastic_reconstructive_activities(request):
    year = datetime.now().year
    activities = SurgeryActivity.objects.filter(
        fraternity="Plastic And Reconstructive Surgery",
        year=year
    ).annotate(
        period_order=Case(
            When(period='Jan-Jun', then=1),
            When(period='Jul-Dec', then=2),
            default=3,
            output_field=IntegerField()
        )
    ).order_by('period_order')
    
    return render(request, 'accounts/plastic_reconstructive_activities.html', {
        'activities': activities,
        'year': year,
    })

@login_required
def add_plastic_reconstructive_activity(request):
    profile = getattr(request.user, 'profile', None)
    if not request.user.is_superuser and (not profile or profile.bidang_pembedahan != 'PLASTIC AND RECONSTRUCTIVE SURGERY'):
        messages.error(request, "You do not have permission to add this activity.")
        return redirect('plastic_reconstructive_activities')

    current_year = datetime.now().year
    existing = SurgeryActivity.objects.filter(
        fraternity="Plastic And Reconstructive Surgery",
        year=current_year
    ).count()

    if existing == 0:
        period = "Jan-Jun"
    elif existing == 1:
        period = "Jul-Dec"
    else:
        messages.error(request, "The activities for this year are already complete.")
        return redirect('plastic_reconstructive_activities')

    activity, created = SurgeryActivity.objects.get_or_create(
        fraternity="Plastic And Reconstructive Surgery",
        year=current_year,
        period=period,
        defaults={'status': 'not_started'}
    )
    activity.users.add(request.user)
    messages.success(request, f"Activity {period} {current_year} created successfully!")
    return redirect('plastic_reconstructive_activities')

@login_required
def form_plastic_reconstructive(request, activity_id):
    profile = getattr(request.user, 'profile', None)
    if not request.user.is_superuser and (not profile or profile.bidang_pembedahan != 'PLASTIC AND RECONSTRUCTIVE SURGERY'):
        messages.error(request, "You do not have permission to access this form.")
        return redirect('plastic_reconstructive_activities')

    activity = get_object_or_404(SurgeryActivity, id=activity_id)

    # Parameter dari Excel PRS (Burn)
    structure_domains = [
        "Establishment and implementation of a standardized burn prevention and first aid program at PKD aligned with National Burn Management Guideline 2024",
        "Operationalisation of a burn prevention and first aid awareness programme at primary healthcare facilities.",
        "Establishment and implementation of hospital-level burn governance and clinical management framework aligned with National Burn Management Guideline 2024",
        "Availability of facilities supporting guideline-based burn first aid and minor burn care",
        "Availability of appropriate hospital facilities to support safe, infection-controlled, and guideline-compliant burn management.",
        "Availability of basic equipment for burn first aid and minor burn management at primary healthcare facilities.",
        "Availability of functional and essential equipment for acute burn management in hospitals",
        "Availability of trained personnel competent in guideline-based burn prevention and first aid education at PKD.",
        "Availability of trained healthcare personnel for burn first aid and minor burn management at primary healthcare facilities",
        "Availability of qualified and trained multidisciplinary workforce for burn management",
        "Availability and utilisation of financial allocation or resource support to ensure continuous delivery of guideline-compliant burn prevention activities and clinical burn care at the primary healthcare level.",
        "Availability of sufficient financial allocation and resource support for comprehensive burn management services in hospitals.",
        "Availability and utilisation of a structured clinical documentation, data recording, and reporting system for burn patient management and prevention activities at primary healthcare facilities.",
        "Availability and utilisation of a comprehensive burn information system, including clinical documentation, burn registry, and audit processes to support quality care and outcome monitoring."
    ]
    
    process_domains = [
        "Percentage of burn patients appropriately assessed and referred according to clinical guidelines at primary healthcare facilities.",
        "Percentage of burn patients with complete initial assessment and early management documentation in compliance with The National Burn Management Guideline 2024",
        "Percentage of burn patients requiring referral who receive appropriate basic stabilization and initial management prior to referral at primary healthcare level.",
        "Percentage of burn patients receiving initial management within 30 minutes of presentation.",
        "Percentage of burn patients undergoing surgical procedures with complete informed consent form prior to intervention",
        "Percentage of burn patients undergoing procedures with complete compliance to MPSG requirements for correct patient, correct procedure, and correct site verification.",
        "Percentage of burn patients undergoing procedures with documented ASA (American Society of Anesthesiologists) classification prior to anesthesia.",
        "Percentage of burn patients with complete and timely submission of ePOMR for outcome monitoring.",
        "Percentage of admitted burn patients managed with appropriate barrier nursing practices in accordance with KKM Infection Prevention and Control (IPC) guidelines"
    ]
    
    outcome_domains = [
        "Percentage of minor burn patients managed at Klinik Kesihatan who receive at least two documented follow-up visits after the initial encounter within the prescribed follow-up period.",
        "Percentage of burn patients discharged from hospital achieve timely continuation of care through outpatient follow-up or appropriate step-down referral within 7 days of discharge.",
        "Percentage of burn patients requiring emergency or urgent first surgical intervention who experience adverse clinical outcomes associated with delay beyond the recommended MOH POMR priority timeframe.",
        "Zero mortality due to burn-related sepsis among patients with 2nd-degree burns (≤ 20% TBSA) without inhalation injury.",
        "Percentage of skin grafting procedures achieving ≥ 90% graft take (successful adherence) at the first objective assessment.",
        "Achieving a minimum 80% patient satisfaction rate regarding the referral process and major burn care management.",
        "Equitable availability of essential burn wound care dressings via current Approved Product Purchase List (APPL) at primary healthcare facilities.",
        "Equitable achievement of hospital-level burn care standards nationwide."
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
        return redirect('plastic_reconstructive_activities')

    return render(request, "accounts/form_plastic_reconstructive.html", {
        "activity": activity,
        "structure_domains": structure_domains,
        "process_domains": process_domains,
        "outcome_domains": outcome_domains,
        "detail_dict": detail_dict,
    })

@login_required
def dashboard_plastic_reconstructive(request):
    selected_year = int(request.GET.get('year', datetime.now().year))
    selected_period = request.GET.get('period', 'Jan-Jun')

    activities = SurgeryActivity.objects.filter(
        fraternity="Plastic And Reconstructive Surgery",
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
        return render(request, "accounts/dashboard_plastic_reconstructive.html", context)

    activity = activities.first()
    details = SurgeryActivityDetail.objects.filter(activity=activity)

    total_structure_raw = min(float(sum(details.filter(category="structure").values_list("weighted_score", flat=True)) or 0.0), 1.0)
    total_process_raw = min(float(sum(details.filter(category="process").values_list("weighted_score", flat=True)) or 0.0), 1.0)
    total_outcome_raw = min(float(sum(details.filter(category="outcome").values_list("weighted_score", flat=True)) or 0.0), 1.0)

    # Pemberat PRS (Burn): 90% Structure, 5% Process, 5% Outcome
    total_structure = total_structure_raw * 0.90
    total_process = total_process_raw * 0.05
    total_outcome = total_outcome_raw * 0.05
    overall_index = min(total_structure + total_process + total_outcome, 1.0)

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
        "total_process_raw": round(total_process_raw, 2),
        "total_outcome_raw": round(total_outcome_raw, 2),
        "total_structure": round(total_structure, 2),
        "total_process": round(total_process, 2),
        "total_outcome": round(total_outcome, 2),
        "overall_index": round(overall_index, 2),
        "domain_rows": domain_rows,
        "years": list(range(2020, datetime.now().year + 2)),
        "selected_year": selected_year,
        "selected_period": selected_period,
    }
    return render(request, "accounts/dashboard_plastic_reconstructive.html", context)

# =============================================
# ORAL MAXILLOFACIAL SURGERY (DENTAL ODO)
# =============================================
@login_required
def oral_maxillofacial(request):
    return render(request, 'accounts/oral_maxillofacial.html')

@login_required
def oral_maxillofacial_activities(request):
    year = datetime.now().year
    activities = SurgeryActivity.objects.filter(
        fraternity="Oral Maxillofacial Surgery",
        year=year
    ).annotate(
        period_order=Case(
            When(period='Jan-Jun', then=1),
            When(period='Jul-Dec', then=2),
            default=3,
            output_field=IntegerField()
        )
    ).order_by('period_order')
    
    return render(request, 'accounts/oral_maxillofacial_activities.html', {
        'activities': activities,
        'year': year,
    })

@login_required
def add_oral_maxillofacial_activity(request):
    profile = getattr(request.user, 'profile', None)
    if not request.user.is_superuser and (not profile or profile.bidang_pembedahan != 'ORAL MAXILLOFACIAL SURGERY'):
        messages.error(request, "You do not have permission to add this activity.")
        return redirect('oral_maxillofacial_activities')

    current_year = datetime.now().year
    existing = SurgeryActivity.objects.filter(
        fraternity="Oral Maxillofacial Surgery",
        year=current_year
    ).count()

    if existing == 0:
        period = "Jan-Jun"
    elif existing == 1:
        period = "Jul-Dec"
    else:
        messages.error(request, "The activities for this year are already complete.")
        return redirect('oral_maxillofacial_activities')

    activity, created = SurgeryActivity.objects.get_or_create(
        fraternity="Oral Maxillofacial Surgery",
        year=current_year,
        period=period,
        defaults={'status': 'not_started'}
    )
    activity.users.add(request.user)
    messages.success(request, f"Activity {period} {current_year} created successfully!")
    return redirect('oral_maxillofacial_activities')

@login_required
def form_oral_maxillofacial(request, activity_id):
    profile = getattr(request.user, 'profile', None)
    if not request.user.is_superuser and (not profile or profile.bidang_pembedahan != 'ORAL MAXILLOFACIAL SURGERY'):
        messages.error(request, "You do not have permission to access this form.")
        return redirect('oral_maxillofacial_activities')

    activity = get_object_or_404(SurgeryActivity, id=activity_id)

    # Parameter Diekstrak dari Excel "NSAPR Dental Odo Final"
    structure_domains = [
        "Development on health training module for odontogenic infections / Development of updated SOP/referral pathway",
        "Percentage of Oral Health Programs with Odontogenic Infections Component / % of DO underwent health training module / Establishment the norm requirement for OMFS beds",
        "% of Dental Clinics having Oral Health Education Materials / Continuous Availability of Essential Antibiotics / All hospital with in-house OMFS must have imaging equipment",
        "Involvement of Dental Public Health Specialists, Dental officers and Dental therapists in delivering oral health education / Availability of on-call OMFS specialist team",
        "Availability of Dedicated Budget Allocation for Management of Odontogenic Infections / Percentage of Districts with Dedicated Annual Budget Allocation",
        "Digitalization (General)"
    ]
    
    process_domains = [
        "Percentage of Odontogenic Infections with Documented Vital Signs and Risk Assessment / % of appropriate referral according to guideline",
        "Percentage of Primary Care DO Trained in Preoperative Risk Assessment / % of airway involvement at time of presentation to OMFS",
        "% of referrals accompanied by completed referral form",
        "Intraoperative Surgical Safety Checklist Compliance Rate / % of full adherence to SSSL",
        "Intraoperative - Anaesthesia Safety (General)",
        "% of deaths due to odontogenic infection",
        "% of rural/underserved community received oral health education on odontogenic infections"
    ]
    
    outcome_domains = [
        "Percentages of participants who are aware of the red flag symptoms of odontogenic infections",
        "Percentages of participants who know where to seek early care for odontogenic infections",
        "Mortality rate due to odontogenic infection",
        "Surgical Site Infection (General)",
        "% of patients reporting satisfaction with management and explanation given",
        "Equity (General)"
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
                
                try: num_val = float(performances) if performances else 0.0
                except ValueError: num_val = 0.0
                
                try: den_val = float(denominator) if denominator else 0.0
                except ValueError: den_val = 0.0
                
                try: tgt_val = float(target) if target else 0.0
                except ValueError: tgt_val = 0.0

                calc_divisor = den_val if den_val > 0 else tgt_val
                score_f, wscore_f, index_f = calculate_domain_scores(num_val, calc_divisor, weight)

                SurgeryActivityDetail.objects.create(
                    activity=activity,
                    category=category_name,
                    domain=domain,
                    performances_value=num_val,
                    denominator=den_val,
                    target=tgt_val,
                    weight=float(weight) if weight else 0.0,
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
        return redirect('oral_maxillofacial_activities')

    return render(request, "accounts/form_oral_maxillofacial.html", {
        "activity": activity,
        "structure_domains": structure_domains,
        "process_domains": process_domains,
        "outcome_domains": outcome_domains,
        "detail_dict": detail_dict,
    })

@login_required
def dashboard_oral_maxillofacial(request):
    selected_year = int(request.GET.get('year', datetime.now().year))
    selected_period = request.GET.get('period', 'Jan-Jun')

    activities = SurgeryActivity.objects.filter(
        fraternity="Oral Maxillofacial Surgery",
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
        return render(request, "accounts/dashboard_oral_maxillofacial.html", context)

    activity = activities.first()
    details = SurgeryActivityDetail.objects.filter(activity=activity)

    total_structure_raw = min(float(sum(details.filter(category="structure").values_list("weighted_score", flat=True)) or 0.0), 1.0)
    total_process_raw = min(float(sum(details.filter(category="process").values_list("weighted_score", flat=True)) or 0.0), 1.0)
    total_outcome_raw = min(float(sum(details.filter(category="outcome").values_list("weighted_score", flat=True)) or 0.0), 1.0)

    # Pemberat Dental (Odo): 50% Structure, 30% Process, 20% Outcome
    total_structure = total_structure_raw * 0.50
    total_process = total_process_raw * 0.30
    total_outcome = total_outcome_raw * 0.20
    overall_index = min(total_structure + total_process + total_outcome, 1.0)

    domain_rows = [{
        "category": d.category.capitalize(),
        "domain": d.domain,
        "performances_value": d.performances_value,
        "denominator": d.denominator,
        "target": d.target,
        "weight": d.weight,
        "score": d.score,
        "weighted_score": d.weighted_score,
        "index": d.index,
    } for d in details]

    context = {
        "total_structure_raw": round(total_structure_raw, 2),
        "total_process_raw": round(total_process_raw, 2),
        "total_outcome_raw": round(total_outcome_raw, 2),
        "total_structure": round(total_structure, 2),
        "total_process": round(total_process, 2),
        "total_outcome": round(total_outcome, 2),
        "overall_index": round(overall_index, 2),
        "domain_rows": domain_rows,
        "years": list(range(2020, datetime.now().year + 2)),
        "selected_year": selected_year,
        "selected_period": selected_period,
    }
    return render(request, "accounts/dashboard_oral_maxillofacial.html", context)

@login_required
def public_health(request):
    return render(request, 'accounts/public_health.html')

# =============================================
# FAMILY MEDICINE (FMS)
# =============================================
@login_required
def family_medicine(request):
    return render(request, 'accounts/family_medicine.html')

@login_required
def family_medicine_activities(request):
    year = datetime.now().year
    activities = SurgeryActivity.objects.filter(
        fraternity="Family Medicine",
        year=year
    ).annotate(
        period_order=Case(
            When(period='Jan-Jun', then=1),
            When(period='Jul-Dec', then=2),
            default=3,
            output_field=IntegerField()
        )
    ).order_by('period_order')
    return render(request, 'accounts/family_medicine_activities.html', {
        'activities': activities,
        'year': year,
    })

@login_required
def add_family_medicine_activity(request):
    profile = getattr(request.user, 'profile', None)
    if not request.user.is_superuser and (not profile or profile.bidang_pembedahan != 'FAMILY MEDICINE'):
        messages.error(request, "You do not have permission to add this activity.")
        return redirect('family_medicine_activities')

    current_year = datetime.now().year
    existing = SurgeryActivity.objects.filter(
        fraternity="Family Medicine",
        year=current_year
    ).count()

    if existing == 0:
        period = "Jan-Jun"
    elif existing == 1:
        period = "Jul-Dec"
    else:
        messages.error(request, "The activities for this year are already complete.")
        return redirect('family_medicine_activities')

    activity, created = SurgeryActivity.objects.get_or_create(
        fraternity="Family Medicine",
        year=current_year,
        period=period,
        defaults={'status': 'not_started'}
    )
    activity.users.add(request.user)
    messages.success(request, f"Activity {period} {current_year} created successfully!")
    return redirect('family_medicine_activities')

@login_required
def form_family_medicine(request, activity_id):
    profile = getattr(request.user, 'profile', None)
    if not request.user.is_superuser and (not profile or profile.bidang_pembedahan != 'FAMILY MEDICINE'):
        messages.error(request, "You do not have permission to access this form.")
        return redirect('family_medicine_activities')

    activity = get_object_or_404(SurgeryActivity, id=activity_id)

    # Parameter Terbaharu dari Excel (NSAPR FMS (Breast Ca) Final)
    structure_domains = [
        "Number of functional mobile screening units providing breast cancer assessment",
        "Establishment of a structured Pink Ribbon Programme at national and state levels",
        "Create policy on risk assessment screening tools and referral pathway",
        "Create educational module and tools for breast cancer for HCP, patients and NGO",
        "Development of training modules for healthcare providers (HCP) to function as patient navigators",
        "Dedicated financial allocation to support capacity building, infrastructure, and digital systems",
        "Establishment of a referral tracking system including digital patient records and reminder"
    ]
    process_domains = [
        "Create risk assessment screening tools and referral pathway for primary care",
        "Percentage of suspicious breast cancer cases appropriately referred from primary care to tertiary centres",
        "Percentage of breast cancer patients receiving appropriate preoperative optimisation prior to surgery"
    ]
    outcome_domains = [
        "Establish patient satisfaction survey regarding communication, waiting time, involvement in care planning",
        "Percentage of referred women who attended breast specialist clinic"
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
        return redirect('family_medicine_activities')

    return render(request, "accounts/form_family_medicine.html", {
        "activity": activity,
        "structure_domains": structure_domains,
        "process_domains": process_domains,
        "outcome_domains": outcome_domains,
        "detail_dict": detail_dict,
    })

@login_required
def dashboard_family_medicine(request):
    selected_year = int(request.GET.get('year', datetime.now().year))
    selected_period = request.GET.get('period', 'Jan-Jun')

    activities = SurgeryActivity.objects.filter(
        fraternity="Family Medicine",
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
        return render(request, "accounts/dashboard_family_medicine.html", context)

    activity = activities.first()
    details = SurgeryActivityDetail.objects.filter(activity=activity)

    total_structure_raw = min(float(sum(details.filter(category="structure").values_list("weighted_score", flat=True)) or 0.0), 1.0)
    total_process_raw = min(float(sum(details.filter(category="process").values_list("weighted_score", flat=True)) or 0.0), 1.0)
    total_outcome_raw = min(float(sum(details.filter(category="outcome").values_list("weighted_score", flat=True)) or 0.0), 1.0)

    # Pemberat FMS: 50% Structure, 30% Process, 20% Outcome (Mengikut Excel)
    total_structure = total_structure_raw * 0.5
    total_process = total_process_raw * 0.3
    total_outcome = total_outcome_raw * 0.2
    overall_index = min(total_structure + total_process + total_outcome, 1.0)

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
        "total_process_raw": round(total_process_raw, 2),
        "total_outcome_raw": round(total_outcome_raw, 2),
        "total_structure": round(total_structure, 2),
        "total_process": round(total_process, 2),
        "total_outcome": round(total_outcome, 2),
        "overall_index": round(overall_index, 2),
        "domain_rows": domain_rows,
        "years": list(range(2020, datetime.now().year + 2)),
        "selected_year": selected_year,
        "selected_period": selected_period,
    }
    return render(request, "accounts/dashboard_family_medicine.html", context)