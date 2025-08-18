import mimetypes

from django.db import models

# Create your models here.
class Document(models.Model):
    id = models.AutoField(primary_key=True)
    file_name = models.CharField(max_length=100)
    creation_date = models.DateTimeField(auto_now_add=True)
    data = models.TextField(null=True, blank=True)
    file = models.FileField(upload_to='files/', null=True, blank=True)
    file_size = models.CharField(max_length=50, blank=True)  # auto set
    content_type = models.CharField(max_length=100, blank=True)  # auto set

    def save(self, *args, **kwargs):
        # If file is uploaded, set file size and content type
        if self.file and hasattr(self.file, 'size'):
            # Auto set file size
            size_bytes = self.file.size
            self.file_size = self._human_readable_size(size_bytes)

            # Auto set content type (MIME type)
            mime_type, _ = mimetypes.guess_type(self.file.name)
            if mime_type:
                self.content_type = mime_type

        super().save(*args, **kwargs)

    def _human_readable_size(self, size):
        """Convert bytes to human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024

    class Meta:
        db_table = "document"
        verbose_name = "document"
        verbose_name_plural = "documents"