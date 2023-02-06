export default {
  getExtensionByMimetype: (mimetype) => {
    switch (mimetype) {
      case 'image/png':
        return 'png'
      case 'image/gif':
        return 'gif'
      case 'image/jpeg':
        return 'jpg';
      case 'application/pdf':
        return 'pdf';
      case 'application/msword':
        return 'doc'
      case 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
        return 'docx'
      case 'application/vnd.ms-powerpoint':
        return 'ppt'
      case 'application/vnd.openxmlformats-officedocument.presentationml.presentation':
        return 'pptx'
      case 'application/vnd.ms-excel':
        return 'xls'
      case 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
        return 'xlsx'
      case 'application/zip':
        return 'zip'
      case 'text/plain':
        return 'txt'
      case 'text/csv':
        return 'csv'
      default:
        return '';
    }
  },
}

