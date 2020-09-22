from apps.core.models import File


def get_file(pk):
    try:
        return File.objects.get(pk=pk).file
    except:
        return None
