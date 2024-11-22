import os

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from dotenv import load_dotenv

load_dotenv()


class ObjectStorageClient:
    def __init__(self) -> None:
        self.s3_client = boto3.client(
            service_name="s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
            aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
            region_name=os.getenv("REGION_NAME"),
            endpoint_url=os.getenv("ENDPOINT_URL"),
        )

    def create_bucket(self, bucket_name: str) -> bool:
        """NCP object storage bucket 생성"""
        from botocore.exceptions import ClientError

        try:
            self.s3_client.create_bucket(Bucket=bucket_name)
            print(f"{bucket_name} 버킷이 생성되었습니다.")
            return True
        except ClientError as e:
            print(f"{bucket_name} 생성에 실패하였습니다: {e}")
            return False

    def upload_file(self, bucket_name: str, file_path: str, object_name: str | None = None) -> str | None:
        """특정 버킷에 파일 업로드"""
        if object_name is None:
            object_name = file_path.split("/")[-1]

        try:
            self.s3_client.upload_file(file_path, bucket_name, object_name)
            print(f"{file_path} 파일이 {object_name} 으로 {bucket_name}에 저장되었습니다.")
            return f"{self.s3_client.meta.endpoint_url}/{bucket_name}/{object_name}"
        except FileNotFoundError:
            print(f"{file_path} 가 없습니다.")
            return None
        except NoCredentialsError:
            print("Credentials not available.")
            return None
        except ClientError as e:
            print(f"Failed to upload file '{file_path}': {e}")
            return None

    def find_bucket(self, bucket_name: str) -> None:
        """지정된 버킷의 모든 객체와 최상위 폴더 및 파일 목록을 출력"""
        try:
            max_keys = 300

            # 버킷 내 모든 객체 나열
            print("Listing all objects in the bucket:")
            response = self.s3_client.list_objects(Bucket=bucket_name, MaxKeys=max_keys)

            while True:
                print(f"IsTruncated={response.get('IsTruncated')}")
                print(f"Marker={response.get('Marker')}")
                print(f"NextMarker={response.get('NextMarker')}")

                print("Object List:")
                for content in response.get("Contents", []):
                    print(
                        f" Name={content.get('Key')}, Size={content.get('Size')}, Owner={content.get('Owner', {}).get('ID')}"
                    )

                if response.get("IsTruncated"):
                    response = self.s3_client.list_objects(
                        Bucket=bucket_name, MaxKeys=max_keys, Marker=response.get("NextMarker")
                    )
                else:
                    break

            # 최상위 폴더와 파일 나열
            delimiter = "/"
            response = self.s3_client.list_objects(Bucket=bucket_name, Delimiter=delimiter, MaxKeys=max_keys)

            print("Top level folders and files in the bucket:")
            while True:
                print(f"IsTruncated={response.get('IsTruncated')}")
                print(f"Marker={response.get('Marker')}")
                print(f"NextMarker={response.get('NextMarker')}")

                print("Folder List:")
                for folder in response.get("CommonPrefixes", []):
                    print(f" Name={folder.get('Prefix')}")

                print("File List:")
                for content in response.get("Contents", []):
                    print(
                        f" Name={content.get('Key')}, Size={content.get('Size')}, Owner={content.get('Owner', {})
                          .get('ID')}"
                    )

                if response.get("IsTruncated"):
                    response = self.s3_client.list_objects(
                        Bucket=bucket_name, Delimiter=delimiter, MaxKeys=max_keys, Marker=response.get("NextMarker")
                    )
                else:
                    break

        except self.s3_client.exceptions.NoSuchBucket:
            print(f"Bucket '{bucket_name}' does not exist.")
        except ClientError as e:
            print(f"An error occurred: {e}")

    def download_file(self, bucket_name: str, object_name: str, local_file_path: str) -> bool:
        try:
            self.s3_client.download_file(bucket_name, object_name, local_file_path)
            print(f"{object_name} 파일이 {local_file_path} 경로에 다운로드 되었습니다.")
            return True

        except FileNotFoundError:
            print(f"{object_name} 파일을 찾을 수 없습니다.")
            return False
        except NoCredentialsError:
            print("자격 증명을 사용할 수 없습니다.")
            return False
        except ClientError as e:
            print(f"{object_name} 다운로드에 실패하였습니다. {e}")
            return False

    def delete_file(self, bucket_name: str, object_name: str) -> bool:
        try:
            self.s3_client.delete_object(Bucket=bucket_name, Key=object_name)
            print(f"{object_name}이 삭제되었습니다.")
            return True
        except FileNotFoundError:
            print(f"{object_name} 파일을 찾을 수 없습니다.")
            return False
        except NoCredentialsError:
            print("자격 증명을 사용할 수 없습니다.")
            return False
        except ClientError as e:
            print(f"{object_name} 삭제에 실패하였습니다. {e}")
            return False
