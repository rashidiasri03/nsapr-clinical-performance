from django.urls import path
from . import views
from .views import login_view, logout_view, fraternity, general_surgery_activities,  register_user, general_surgery,form_gs,add_gs_activity,main
urlpatterns = [
    path('main/',main, name='main'),
    path('journey/', views.journey, name='journey'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('fraternity/', fraternity, name='fraternity'),
    path('general_surgery/', general_surgery, name='general_surgery'),  # page Surgery
    path('general_surgery_activities/', general_surgery_activities, name='general_surgery_activities'),
    path('dashboard_gs/', views.dashboard_gs, name='dashboard_gs'),
    path('register-user/', register_user, name='register_user'),
    path('fraternity/general-surgery/form/<int:activity_id>/', form_gs, name='form_gs'),
    path("add-gs-activity/", add_gs_activity, name="add_gs_activity"),

       # General Surgery Colorectal
    path('gscolorectal/', views.gscolorectal, name='gscolorectal'),
    path('gscolorectal/activities/', views.gscolorectal_activities, name='gscolorectal_activities'),
    path('gscolorectal/add/', views.add_gscolorectal_activity, name='add_gscolorectal_activity'),
    path('gscolorectal/form/<int:activity_id>/', views.form_gscolorectal, name='form_gscolorectal'),
    path('gscolorectal/dashboard/', views.dashboard_gscolorectal, name='dashboard_gscolorectal'),

       # GS Breast & Endocrine
    path("gsbreast-endocrine/", views.gsbreast_endocrine, name="gsbreast_endocrine"),
    path("gsbreast-endocrine/activities/", views.gsbreast_endocrine_activities, name="gsbreast_endocrine_activities"),
    path("gsbreast-endocrine/add/", views.add_gsbreast_endocrine_activity, name="add_gsbreast_endocrine_activity"),
    path("gsbreast-endocrine/form/<int:activity_id>/", views.form_gsbreast_endocrine, name="form_gsbreast_endocrine"),
    path("gsbreast-endocrine/dashboard/", views.dashboard_gsbreast_endocrine, name="dashboard_gsbreast_endocrine"),
       # GS Breast & Endocrine
    path('gsvascular/', views.gsvascular, name='gsvascular'),
    path('gsvascular/activities/', views.gsvascular_activities, name='gsvascular_activities'),
    path('gsvascular/add/', views.add_gsvascular_activity, name='add_gsvascular_activity'),
    path('gsvascular/form/<int:activity_id>/', views.form_gsvascular, name='form_gsvascular'),
    path('gsvascular/dashboard/', views.dashboard_gsvascular, name='dashboard_gsvascular'),

    # GS Hepatobiliary
    path("gshepatobiliary/", views.gshepatobiliary, name="gshepatobiliary"),
    path("gshepatobiliary/activities/", views.gshepatobiliary_activities, name="gshepatobiliary_activities"),
    path("gshepatobiliary/add/", views.add_gshepatobiliary_activity, name="add_gshepatobiliary_activity"),
    path("gshepatobiliary/delete/<int:activity_id>/", views.delete_gshepatobiliary_activity, name="delete_gshepatobiliary_activity"),
    path("gshepatobiliary/form/<int:activity_id>/", views.form_gshepatobiliary, name="form_gshepatobiliary"),
    path("gshepatobiliary/dashboard/", views.dashboard_gshepatobiliary, name="dashboard_gshepatobiliary"),

    # GS Thoracic
    path("gsthoracic/", views.gsthoracic, name="gsthoracic"),
    path("gsthoracic/activities/", views.gsthoracic_activities, name="gsthoracic_activities"),
    path("gsthoracic/add/", views.add_gsthoracic_activity, name="add_gsthoracic_activity"),
    path("gsthoracic/form/<int:activity_id>/", views.form_gsthoracic, name="form_gsthoracic"),
    path("gsthoracic/dashboard/", views.dashboard_gsthoracic, name="dashboard_gsthoracic"),

    path("gstrauma/", views.gstrauma, name="gstrauma"),
    #path("gscolorectal_activities/", views.gscolorectal_activities, name="gscolorectal_activities"),
    #path("add-gscolorectal-activity/", views.add_gscolorectal_activity, name="add_gscolorectal_activity"),
    #path("fraternity/gscolorectal/form/<int:activity_id>/", views.form_gscolorectal, name="form_gscolorectal"),

    path("upper-gi/", views.upper_gi, name="upper_gi"),
    path("upper-gi/activities/", views.upper_gi_activities, name="upper_gi_activities"),
    path("upper-gi/add/", views.add_upper_gi_activity, name="add_upper_gi_activity"),
    path("upper-gi/form/<int:activity_id>/", views.form_upper_gi, name="form_upper_gi"),
    path("upper-gi/dashboard/", views.dashboard_upper_gi, name="dashboard_upper_gi"),

    path("anaesthesia/", views.anaesthesia, name="anaesthesia"),
    path("anaesthesia/activities/", views.anaesthesia_activities, name="anaesthesia_activities"),
    path("anaesthesia/add/", views.add_anaesthesia_activity, name="add_anaesthesia_activity"),
    path("anaesthesia/delete/<int:activity_id>/", views.delete_anaesthesia_activity, name="delete_anaesthesia_activity"),
    path("anaesthesia/form/<int:activity_id>/", views.form_anaesthesia, name="form_anaesthesia"),
    path("anaesthesia/dashboard/", views.dashboard_anaesthesia, name="dashboard_anaesthesia"),

    path("orthopaedic/", views.orthopaedic, name="orthopaedic"),
    #path("gscolorectal_activities/", views.gscolorectal_activities, name="gscolorectal_activities"),
    #path("add-gscolorectal-activity/", views.add_gscolorectal_activity, name="add_gscolorectal_activity"),
    #path("fraternity/gscolorectal/form/<int:activity_id>/", views.form_gscolorectal, name="form_gscolorectal"),

    path("neurosurgery/", views.neurosurgery, name="neurosurgery"),
    #path("gscolorectal_activities/", views.gscolorectal_activities, name="gscolorectal_activities"),
    #path("add-gscolorectal-activity/", views.add_gscolorectal_activity, name="add_gscolorectal_activity"),
    #path("fraternity/gscolorectal/form/<int:activity_id>/", views.form_gscolorectal, name="form_gscolorectal"),

    path("urology/", views.urology, name="urology"),
    #path("gscolorectal_activities/", views.gscolorectal_activities, name="gscolorectal_activities"),
    #path("add-gscolorectal-activity/", views.add_gscolorectal_activity, name="add_gscolorectal_activity"),
    #path("fraternity/gscolorectal/form/<int:activity_id>/", views.form_gscolorectal, name="form_gscolorectal"),

    # PAEDIATRIC SURGERY
    path("paediatric/", views.paediatric, name="paediatric"),
    path("paediatric/activities/", views.paediatric_activities, name="paediatric_activities"),
    path("paediatric/add/", views.add_paediatric_activity, name="add_paediatric_activity"),
    path("paediatric/delete/<int:activity_id>/", views.delete_paediatric_activity, name="delete_paediatric_activity"),
    path("paediatric/form/<int:activity_id>/", views.form_paediatric, name="form_paediatric"),
    path("paediatric/dashboard/", views.dashboard_paediatric, name="dashboard_paediatric"),

    path("cardiothoracic/", views.cardiothoracic, name="cardiothoracic"),
    #path("gscolorectal_activities/", views.gscolorectal_activities, name="gscolorectal_activities"),
    #path("add-gscolorectal-activity/", views.add_gscolorectal_activity, name="add_gscolorectal_activity"),
    #path("fraternity/gscolorectal/form/<int:activity_id>/", views.form_gscolorectal, name="form_gscolorectal"),

    path("obstetrics_gynaecology/", views.obstetrics_gynaecology, name="obstetrics_gynaecology"),
    #path("gscolorectal_activities/", views.gscolorectal_activities, name="gscolorectal_activities"),
    #path("add-gscolorectal-activity/", views.add_gscolorectal_activity, name="add_gscolorectal_activity"),
    #path("fraternity/gscolorectal/form/<int:activity_id>/", views.form_gscolorectal, name="form_gscolorectal"),

    path("ophthalmology/", views.ophthalmology, name="ophthalmology"),
    path("ophthalmology_activities/", views.ophthalmology_activities, name="ophthalmology_activities"),
    path("add-ophthalmology-activity/", views.add_ophthalmology_activity, name="add_ophthalmology_activity"),
    path("fraternity/ophthalmology/form/<int:activity_id>/", views.form_ophthalmology, name="form_ophthalmology"),
    path('dashboard_opththalmology/', views.dashboard_ophthalmology, name='dashboard_opththalmology'),

    
    path("otorhinolaryngology/", views.otorhinolaryngology, name="otorhinolaryngology"),
    #path("gscolorectal_activities/", views.gscolorectal_activities, name="gscolorectal_activities"),
    #path("add-gscolorectal-activity/", views.add_gscolorectal_activity, name="add_gscolorectal_activity"),
    #path("fraternity/gscolorectal/form/<int:activity_id>/", views.form_gscolorectal, name="form_gscolorectal"),

    path("plastic_reconstructive/", views.plastic_reconstructive, name="plastic_reconstructive"),
    #path("gscolorectal_activities/", views.gscolorectal_activities, name="gscolorectal_activities"),
    #path("add-gscolorectal-activity/", views.add_gscolorectal_activity, name="add_gscolorectal_activity"),
    #path("fraternity/gscolorectal/form/<int:activity_id>/", views.form_gscolorectal, name="form_gscolorectal"),

    path("emergency-trauma/", views.emergency_trauma, name="emergency_trauma"),
    path("emergency-trauma/activities/", views.emergency_trauma_activities, name="emergency_trauma_activities"),
    path("emergency-trauma/add/", views.add_emergency_trauma_activity, name="add_emergency_trauma_activity"),
    path("emergency-trauma/form/<int:activity_id>/", views.form_emergency_trauma, name="form_emergency_trauma"),
    path("emergency-trauma/dashboard/", views.dashboard_emergency_trauma, name="dashboard_emergency_trauma"),

    path("oral_maxillofacial/", views.oral_maxillofacial, name="oral_maxillofacial"),
    #path("gscolorectal_activities/", views.gscolorectal_activities, name="gscolorectal_activities"),
    #path("add-gscolorectal-activity/", views.add_gscolorectal_activity, name="add_gscolorectal_activity"),
    #path("fraternity/gscolorectal/form/<int:activity_id>/", views.form_gscolorectal, name="form_gscolorectal"),

    path("public_health/", views.public_health, name="public_health"),
    #path("gscolorectal_activities/", views.gscolorectal_activities, name="gscolorectal_activities"),
    #path("add-gscolorectal-activity/", views.add_gscolorectal_activity, name="add_gscolorectal_activity"),
    #path("fraternity/gscolorectal/form/<int:activity_id>/", views.form_gscolorectal, name="form_gscolorectal"),

    path("family_medicine/", views.family_medicine, name="family_medicine"),
    #path("gscolorectal_activities/", views.gscolorectal_activities, name="gscolorectal_activities"),
    #path("add-gscolorectal-activity/", views.add_gscolorectal_activity, name="add_gscolorectal_activity"),
    #path("fraternity/gscolorectal/form/<int:activity_id>/", views.form_gscolorectal, name="form_gscolorectal"),






]