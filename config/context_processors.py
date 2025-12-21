from settings.models import CompanySettings

def company_settings(request):
    """
    Context processor to make company settings available in all templates
    """
    settings = CompanySettings.get_settings()
    
    return {
        'company_settings': settings,
        'company_name': settings.company_name_ar or 'اسم المؤسسة',
        "company_logo": logo_url,
    }