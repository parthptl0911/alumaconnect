def site_settings(request):
    """
    Returns global site settings to be used in all templates.
    """
    return {
        'site_name': 'AlumaConnect'
    }
