#!/usr/bin/env python3
"""
Nextcloud WebDAV file management client.

Uses user ID (not username) for WebDAV paths as per Nextcloud requirements.
"""

import os
import sys
import json
import urllib.parse
from pathlib import Path

try:
    import requests
    from requests.auth import HTTPBasicAuth
except ImportError:
    raise ImportError("'requests' library required. Install with: pip install requests")


class NextcloudClient:
    """Client for Nextcloud WebDAV operations."""

    def __init__(self):
        """Initialize client from environment variables."""
        self.url = os.environ.get('NEXTCLOUD_URL', '').rstrip('/')
        self.username = os.environ.get('NEXTCLOUD_USERNAME', '')
        self.app_password = os.environ.get('NEXTCLOUD_APP_PASSWORD', '')

        if not all([self.url, self.username, self.app_password]):
            raise EnvironmentError(
                "Missing required environment variables: "
                "NEXTCLOUD_URL, NEXTCLOUD_USERNAME, NEXTCLOUD_APP_PASSWORD"
            )

        self.auth = HTTPBasicAuth(self.username, self.app_password)
        self.user_id = None
        self._resolve_user_id()

    def _resolve_user_id(self):
        """Resolve the numeric user ID from Nextcloud OCS API."""
        # Try to get user info from OCS API
        ocs_url = f"{self.url}/ocs/v1.php/cloud/user"
        headers = {'OCS-APIRequest': 'true'}

        try:
            response = requests.get(ocs_url, auth=self.auth, headers=headers, timeout=30)
            if response.status_code == 200:
                # Parse the XML response to get user ID
                import xml.etree.ElementTree as ET
                root = ET.fromstring(response.content)
                # Try to find the id element
                id_elem = root.find('.//id')
                if id_elem is not None and id_elem.text:
                    self.user_id = id_elem.text
                else:
                    # Fallback to username if ID not found
                    self.user_id = self.username
            else:
                # Fallback to username if API fails
                self.user_id = self.username
        except Exception:
            # Fallback to username on any error
            self.user_id = self.username

    def _ocs_request(self, endpoint, params=None):
        """Make an OCS API request.
        
        Args:
            endpoint: OCS endpoint (e.g., '/apps/files_sharing/api/v1/shares')
            params: Optional query parameters
            
        Returns:
            Parsed XML root element or None on error
        """
        import xml.etree.ElementTree as ET
        
        ocs_url = f"{self.url}/ocs/v1.php{endpoint}"
        headers = {'OCS-APIRequest': 'true'}
        
        try:
            response = requests.get(ocs_url, auth=self.auth, headers=headers, 
                                   params=params, timeout=30)
            if response.status_code == 200:
                return ET.fromstring(response.content)
            else:
                print(f"OCS API error: HTTP {response.status_code}")
                return None
        except ET.ParseError as e:
            print(f"OCS XML parse error: {e}")
            return None
        except Exception as e:
            print(f"OCS request error: {e}")
            return None

    def get_shared_with_me(self):
        """Get list of shares shared with the current user.
        
        Returns:
            List of dicts with share info: name, owner, permissions, path, share_type
        """
        import xml.etree.ElementTree as ET
        
        # OCS endpoint for shares shared with me
        root = self._ocs_request('/apps/files_sharing/api/v1/shares', 
                                params={'shared_with_me': 'true'})
        
        if root is None:
            return []
        
        shares = []
        
        # Parse the OCS response
        # Structure: <ocs><data><element>...</element></data></ocs>
        data = root.find('.//data')
        if data is None:
            return []
        
        for elem in data.findall('.//element'):
            share = {}
            
            # Get share ID
            id_elem = elem.find('.//id')
            share['id'] = id_elem.text if id_elem is not None else ''
            
            # Get file target (path in user's filesystem)
            file_target = elem.find('.//file_target')
            share['path'] = file_target.text if file_target is not None else ''
            
            # Get share type (0=user, 1=group, 3=public link, 6=federated)
            share_type = elem.find('.//share_type')
            share['share_type'] = share_type.text if share_type is not None else '0'
            
            # Get owner info
            uid_owner = elem.find('.//uid_owner')
            share['owner'] = uid_owner.text if uid_owner is not None else 'Unknown'
            
            displayname_owner = elem.find('.//displayname_owner')
            share['owner_display'] = displayname_owner.text if displayname_owner is not None else share['owner']
            
            # Get permissions (1=read, 2=update, 4=create, 8=delete, 16=share)
            permissions = elem.find('.//permissions')
            share['permissions'] = self._parse_permissions(permissions.text if permissions is not None else '1')
            
            # Get name (for directory shares, this is the mount point name)
            name_elem = elem.find('.//name')
            if name_elem is not None and name_elem.text:
                share['name'] = name_elem.text
            else:
                # Fallback to path basename
                share['name'] = os.path.basename(share['path'].rstrip('/'))
            
            # Get share time
            stime = elem.find('.//stime')
            share['shared_at'] = stime.text if stime is not None else ''
            
            shares.append(share)
        
        return shares

    def _parse_permissions(self, perm_value):
        """Parse permission bitmask into readable string."""
        try:
            perm = int(perm_value)
        except (ValueError, TypeError):
            return 'unknown'
        
        perms = []
        if perm & 1:
            perms.append('read')
        if perm & 2:
            perms.append('write')
        if perm & 4:
            perms.append('create')
        if perm & 8:
            perms.append('delete')
        if perm & 16:
            perms.append('share')
        
        return '/'.join(perms) if perms else 'none'

    def _get_webdav_base_url(self):
        """Get the WebDAV base URL using user ID."""
        return f"{self.url}/remote.php/dav/files/{urllib.parse.quote(self.user_id, safe='')}"

    def _get_full_url(self, remote_path):
        """Get full WebDAV URL for a remote path."""
        base = self._get_webdav_base_url()
        # Ensure path starts with /
        if not remote_path.startswith('/'):
            remote_path = '/' + remote_path
        # Remove duplicate slashes
        remote_path = '/' + '/'.join(part for part in remote_path.split('/') if part)
        return f"{base}{urllib.parse.quote(remote_path, safe='/')}"

    def list(self, remote_path='/'):
        """List files and folders in a directory."""
        url = self._get_full_url(remote_path)

        headers = {
            'Depth': '1',
            'Content-Type': 'application/xml'
        }

        # PROPFIND request for listing
        propfind_body = '''<?xml version="1.0" encoding="utf-8"?>
<d:propfind xmlns:d="DAV:">
    <d:prop>
        <d:displayname/>
        <d:resourcetype/>
        <d:getcontentlength/>
        <d:getlastmodified/>
        <d:getcontenttype/>
    </d:prop>
</d:propfind>'''

        response = requests.request('PROPFIND', url, auth=self.auth, headers=headers,
                                   data=propfind_body, timeout=60)

        if response.status_code not in (200, 207):
            print(f"Error listing directory: HTTP {response.status_code}")
            return None

        return self._parse_list_response(response.content, remote_path)

    def _parse_list_response(self, content, base_path):
        """Parse WebDAV PROPFIND response."""
        import xml.etree.ElementTree as ET

        try:
            root = ET.fromstring(content)
        except ET.ParseError:
            return []

        results = []
        base_url = self._get_webdav_base_url() + urllib.parse.quote(base_path, safe='/')

        for response_elem in root.findall('.//{DAV:}response'):
            href = response_elem.find('.//{DAV:}href')
            if href is None:
                continue

            # Decode the href
            href_text = urllib.parse.unquote(href.text)

            # Skip the directory itself (only want contents)
            if href_text.rstrip('/') == base_url.rstrip('/'):
                continue

            # Get the filename from href
            name = os.path.basename(urllib.parse.unquote(href.text.rstrip('/')))

            # Check if it's a collection (folder)
            resourcetype = response_elem.find('.//{DAV:}resourcetype')
            is_folder = resourcetype is not None and resourcetype.find('{DAV:}collection') is not None

            # Get content length
            content_length = response_elem.find('.//{DAV:}getcontentlength')
            size = int(content_length.text) if content_length is not None and content_length.text else 0

            # Get last modified
            last_modified = response_elem.find('.//{DAV:}getlastmodified')
            modified = last_modified.text if last_modified is not None else 'Unknown'

            # Get content type
            content_type = response_elem.find('.//{DAV:}getcontenttype')
            mime_type = content_type.text if content_type is not None else ''

            results.append({
                'name': name,
                'type': 'folder' if is_folder else 'file',
                'size': size,
                'modified': modified,
                'mime_type': mime_type,
                'path': href_text
            })

        return results

    def upload(self, local_path, remote_path):
        """Upload a local file to Nextcloud."""
        local_path = Path(local_path)
        if not local_path.exists():
            print(f"Error: Local file not found: {local_path}")
            return False

        url = self._get_full_url(remote_path)

        # If remote path is a directory, append local filename
        if remote_path.endswith('/'):
            remote_path = remote_path + local_path.name
            url = self._get_full_url(remote_path)

        with open(local_path, 'rb') as f:
            response = requests.put(url, auth=self.auth, data=f, timeout=300)

        if response.status_code in (200, 201, 204):
            print(f"Uploaded: {local_path} -> {remote_path}")
            return True
        else:
            print(f"Error uploading file: HTTP {response.status_code}")
            print(response.text)
            return False

    def download(self, remote_path, local_path):
        """Download a file from Nextcloud."""
        url = self._get_full_url(remote_path)

        response = requests.get(url, auth=self.auth, timeout=300, stream=True)

        if response.status_code != 200:
            print(f"Error downloading file: HTTP {response.status_code}")
            return False

        local_path = Path(local_path)

        # If local path is a directory, use remote filename
        if local_path.is_dir():
            remote_name = os.path.basename(urllib.parse.unquote(remote_path))
            local_path = local_path / remote_name

        # Create parent directories if needed
        local_path.parent.mkdir(parents=True, exist_ok=True)

        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"Downloaded: {remote_path} -> {local_path}")
        return True

    def mkdir(self, remote_path):
        """Create a directory on Nextcloud."""
        url = self._get_full_url(remote_path)

        # Ensure path ends with /
        if not url.endswith('/'):
            url += '/'

        response = requests.request('MKCOL', url, auth=self.auth, timeout=60)

        if response.status_code in (200, 201):
            print(f"Created directory: {remote_path}")
            return True
        else:
            print(f"Error creating directory: HTTP {response.status_code}")
            print(response.text)
            return False

    def delete(self, remote_path):
        """Delete a file or directory on Nextcloud."""
        url = self._get_full_url(remote_path)

        response = requests.delete(url, auth=self.auth, timeout=60)

        if response.status_code in (200, 204):
            print(f"Deleted: {remote_path}")
            return True
        else:
            print(f"Error deleting: HTTP {response.status_code}")
            print(response.text)
            return False

    def move(self, source_path, dest_path):
        """Move/rename a file or directory."""
        source_url = self._get_full_url(source_path)
        dest_url = self._get_full_url(dest_path)

        headers = {'Destination': dest_url}

        response = requests.request('MOVE', source_url, auth=self.auth, headers=headers, timeout=60)

        if response.status_code in (200, 201, 204):
            print(f"Moved: {source_path} -> {dest_path}")
            return True
        else:
            print(f"Error moving: HTTP {response.status_code}")
            print(response.text)
            return False

    def copy(self, source_path, dest_path):
        """Copy a file or directory."""
        source_url = self._get_full_url(source_path)
        dest_url = self._get_full_url(dest_path)

        headers = {'Destination': dest_url}

        response = requests.request('COPY', source_url, auth=self.auth, headers=headers, timeout=120)

        if response.status_code in (200, 201, 204):
            print(f"Copied: {source_path} -> {dest_path}")
            return True
        else:
            print(f"Error copying: HTTP {response.status_code}")
            print(response.text)
            return False

    def info(self, remote_path):
        """Get detailed information about a file or directory."""
        url = self._get_full_url(remote_path)

        headers = {
            'Depth': '0',
            'Content-Type': 'application/xml'
        }

        propfind_body = '''<?xml version="1.0" encoding="utf-8"?>
<d:propfind xmlns:d="DAV:" xmlns:oc="http://owncloud.org/ns" xmlns:nc="http://nextcloud.org/ns">
    <d:prop>
        <d:displayname/>
        <d:resourcetype/>
        <d:getcontentlength/>
        <d:getlastmodified/>
        <d:getcontenttype/>
        <d:getetag/>
        <oc:fileid/>
        <oc:size/>
    </d:prop>
</d:propfind>'''

        response = requests.request('PROPFIND', url, auth=self.auth, headers=headers,
                                   data=propfind_body, timeout=60)

        if response.status_code not in (200, 207):
            print(f"Error getting info: HTTP {response.status_code}")
            return None

        return self._parse_info_response(response.content)

    def _parse_info_response(self, content):
        """Parse WebDAV PROPFIND response for single item."""
        import xml.etree.ElementTree as ET

        try:
            root = ET.fromstring(content)
        except ET.ParseError:
            return None

        response_elem = root.find('.//{DAV:}response')
        if response_elem is None:
            return None

        info = {}

        # Get display name
        displayname = response_elem.find('.//{DAV:}displayname')
        info['name'] = displayname.text if displayname is not None else 'Unknown'

        # Check if folder
        resourcetype = response_elem.find('.//{DAV:}resourcetype')
        info['type'] = 'folder' if resourcetype is not None and resourcetype.find('{DAV:}collection') is not None else 'file'

        # Get size
        content_length = response_elem.find('.//{DAV:}getcontentlength')
        info['size'] = int(content_length.text) if content_length is not None and content_length.text else 0

        # For folders, try oc:size
        oc_size = response_elem.find('.//{http://owncloud.org/ns}size')
        if oc_size is not None and oc_size.text:
            info['size'] = int(oc_size.text)

        # Get last modified
        last_modified = response_elem.find('.//{DAV:}getlastmodified')
        info['modified'] = last_modified.text if last_modified is not None else 'Unknown'

        # Get content type
        content_type = response_elem.find('.//{DAV:}getcontenttype')
        info['mime_type'] = content_type.text if content_type is not None else ''

        # Get etag
        etag = response_elem.find('.//{DAV:}getetag')
        info['etag'] = etag.text if etag is not None else ''

        # Get file ID
        file_id = response_elem.find('.//{http://owncloud.org/ns}fileid')
        info['file_id'] = file_id.text if file_id is not None else ''

        return info


def print_json(data):
    """Print data as formatted JSON."""
    print(json.dumps(data, indent=2))


def print_list(results):
    """Print list results in a readable format."""
    if not results:
        print("(empty)")
        return

    # Calculate column widths
    max_name = max(len(r['name']) for r in results) if results else 10
    max_type = 6
    max_size = 10

    # Header
    print(f"{'Name':<{max_name}} {'Type':<{max_type}} {'Size':>{max_size}} {'Modified'}")
    print('-' * (max_name + max_type + max_size + 30))

    # Files and folders
    folders = sorted([r for r in results if r['type'] == 'folder'], key=lambda x: x['name'])
    files = sorted([r for r in results if r['type'] == 'file'], key=lambda x: x['name'])

    for item in folders + files:
        size_str = str(item['size']) if item['type'] == 'file' else '-'
        modified_short = item['modified'][:19] if len(item['modified']) > 19 else item['modified']
        print(f"{item['name']:<{max_name}} {item['type']:<{max_type}} {size_str:>{max_size}} {modified_short}")


def print_info(info):
    """Print info results."""
    if not info:
        print("No info available")
        return

    print(f"Name:      {info.get('name', 'Unknown')}")
    print(f"Type:      {info.get('type', 'Unknown')}")
    print(f"Size:      {info.get('size', 0)} bytes")
    print(f"Modified:  {info.get('modified', 'Unknown')}")
    print(f"MIME:      {info.get('mime_type', 'N/A')}")
    print(f"ETag:      {info.get('etag', 'N/A')}")
    print(f"File ID:   {info.get('file_id', 'N/A')}")


def print_shared(shares):
    """Print shared with me results in a readable format."""
    if not shares:
        print("No shared folders found.")
        return
    
    # Calculate column widths
    max_name = max(len(s.get('name', '')) for s in shares) if shares else 10
    max_owner = max(len(s.get('owner_display', s.get('owner', 'Unknown'))) for s in shares) if shares else 10
    max_perms = max(len(s.get('permissions', '')) for s in shares) if shares else 10
    
    # Ensure minimum widths
    max_name = max(max_name, 10)
    max_owner = max(max_owner, 10)
    max_perms = max(max_perms, 10)
    
    # Header
    print(f"\n\U0001F4C1 Shared with me:")
    print(f"{'Name':<{max_name}}  {'Owner':<{max_owner}}  {'Permissions':<{max_perms}}  {'Path'}")
    print('-' * (max_name + max_owner + max_perms + 50))
    
    # Sort by name
    for share in sorted(shares, key=lambda x: x.get('name', '')):
        owner = share.get('owner_display', share.get('owner', 'Unknown'))
        perms = share.get('permissions', 'unknown')
        path = share.get('path', '/')
        name = share.get('name', 'Unknown')
        
        print(f"{name:<{max_name}}  {owner:<{max_owner}}  {perms:<{max_perms}}  {path}")
    
    print(f"\nTo access a shared folder, use its path from the list above.")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Nextcloud WebDAV Client")
        print()
        print("Usage: nextcloud.py <command> [arguments]")
        print()
        print("Commands:")
        print("  list <remote_path>              List files in directory")
        print("  upload <local> <remote>         Upload file")
        print("  download <remote> <local>       Download file")
        print("  mkdir <remote_path>             Create directory")
        print("  delete <remote_path>            Delete file or directory")
        print("  move <source> <dest>            Move/rename")
        print("  copy <source> <dest>            Copy file or directory")
        print("  info <remote_path>              Get file/directory info")
        print("  shared                          List folders shared with me")
        print()
        print("Set environment variables: NEXTCLOUD_URL, NEXTCLOUD_USERNAME, NEXTCLOUD_APP_PASSWORD")
        sys.exit(1)

    command = sys.argv[1].lower()
    client = NextcloudClient()

    if command == 'list':
        path = sys.argv[2] if len(sys.argv) > 2 else '/'
        results = client.list(path)
        if results is not None:
            print_list(results)
            sys.exit(0)
        sys.exit(4)

    elif command == 'upload':
        if len(sys.argv) < 4:
            print("Usage: nextcloud.py upload <local_path> <remote_path>")
            sys.exit(1)
        success = client.upload(sys.argv[2], sys.argv[3])
        sys.exit(0 if success else 3)

    elif command == 'download':
        if len(sys.argv) < 4:
            print("Usage: nextcloud.py download <remote_path> <local_path>")
            sys.exit(1)
        success = client.download(sys.argv[2], sys.argv[3])
        sys.exit(0 if success else 3)

    elif command == 'mkdir':
        if len(sys.argv) < 3:
            print("Usage: nextcloud.py mkdir <remote_path>")
            sys.exit(1)
        success = client.mkdir(sys.argv[2])
        sys.exit(0 if success else 3)

    elif command == 'delete':
        if len(sys.argv) < 3:
            print("Usage: nextcloud.py delete <remote_path>")
            sys.exit(1)
        success = client.delete(sys.argv[2])
        sys.exit(0 if success else 3)

    elif command == 'move':
        if len(sys.argv) < 4:
            print("Usage: nextcloud.py move <source_path> <dest_path>")
            sys.exit(1)
        success = client.move(sys.argv[2], sys.argv[3])
        sys.exit(0 if success else 3)

    elif command == 'copy':
        if len(sys.argv) < 4:
            print("Usage: nextcloud.py copy <source_path> <dest_path>")
            sys.exit(1)
        success = client.copy(sys.argv[2], sys.argv[3])
        sys.exit(0 if success else 3)

    elif command == 'info':
        if len(sys.argv) < 3:
            print("Usage: nextcloud.py info <remote_path>")
            sys.exit(1)
        info = client.info(sys.argv[2])
        if info:
            print_info(info)
            sys.exit(0)
        sys.exit(4)

    elif command == 'shared':
        shares = client.get_shared_with_me()
        print_shared(shares)
        sys.exit(0 if shares is not None else 4)

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == '__main__':
    main()