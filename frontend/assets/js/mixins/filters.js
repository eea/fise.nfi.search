 const filters = {
  filters: {
    renameLevel(nut) {
      if (!nut) return '';
      return nut.replace(/L\d+/, "Level ");
    },
    nfiExplain(value) {
      if (!value || value.toLowerCase() !== 'nfi') return value;
      return value.replace(/nfi/gi, "National Forest Inventory");
    },
    bytesToSize(bytes) {
      if(typeof bytes == 'number') {
        var sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        if (bytes == 0) return '0 Byte';
        var i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)));
        return Math.round(bytes / Math.pow(1024, i), 2) + ' ' + sizes[i];
      }
      return '';
    },
    fileType(fileName) {
      if(fileName) {
        var splitedNameItems = fileName.split('.')
        var extension = splitedNameItems[splitedNameItems.length - 1];

        return '[ ' + extension + ' ] ';
      }
      return '';
    },
  },
}
export default filters;