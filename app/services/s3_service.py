import uuid
import aioboto3
from botocore.exceptions import ClientError
from app.core.config import settings
from app.core.exceptions import CustomException

class S3Service:
    def __init__(self):
        self.session = aioboto3.Session()

    async def _ensure_bucket_exists(self, client):
        try:
            await client.head_bucket(Bucket=settings.S3_BUCKET_NAME)
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "404":
                await client.create_bucket(Bucket=settings.S3_BUCKET_NAME)
                # Ensure bucket is publicly readable
                policy = {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Sid": "PublicReadGetObject",
                            "Effect": "Allow",
                            "Principal": "*",
                            "Action": ["s3:GetObject"],
                            "Resource": [f"arn:aws:s3:::{settings.S3_BUCKET_NAME}/*"],
                        }
                    ],
                }
                import json
                await client.put_bucket_policy(Bucket=settings.S3_BUCKET_NAME, Policy=json.dumps(policy))
            else:
                pass

    async def upload_file(self, file_content: bytes, file_name: str, content_type: str = "image/jpeg") -> str:
        unique_name = f"{uuid.uuid4()}-{file_name}"
        try:
            async with self.session.client(
                "s3",
                endpoint_url=settings.S3_ENDPOINT_URL,
                aws_access_key_id=settings.S3_ACCESS_KEY,
                aws_secret_access_key=settings.S3_SECRET_KEY,
            ) as client:
                await self._ensure_bucket_exists(client)
                await client.put_object(
                    Bucket=settings.S3_BUCKET_NAME,
                    Key=unique_name,
                    Body=file_content,
                    ContentType=content_type,
                )
            return f"{settings.S3_PUBLIC_URL_PREFIX}/{unique_name}"
        except ClientError as e:
            raise CustomException("s3_upload_error", f"Could not upload file: {str(e)}", status_code=500)

s3_service = S3Service()
