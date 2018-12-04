// TODO Split in single concerns: filters, computeds, methods
function renameLevel(nut) {
  if (!nut) return "";
  return nut.replace(/\D+/, "Level ");
};

function sortArrayOfObjectsByName(a, b) {
  var nameA = a.name.toUpperCase(); // ignore upper and lowercase
  var nameB = b.name.toUpperCase(); // ignore upper and lowercase
  if (nameA < nameB) {
    return -1;
  }
  if (nameA > nameB) {
    return 1;
  }

  // names must be equal
  return 0;
};

// a string with the first few element from the list
function summary(myDataList, noOfResultsInSummary) {
  let result = '';
  const myDataListItems = Object.keys(myDataList);
  const remainingNumberOfResults = myDataListItems.length - noOfResultsInSummary;

  myDataListItems.slice(0, noOfResultsInSummary).map((key) => {
    let name = myDataList[key].displayName || myDataList[key].name;
    result += name + ', ';
  });
  result += '.. + ' + remainingNumberOfResults + ' more';

  return result;
}

function transformFromObjectToArray(dataList) {
  const result = [];

  Object.keys(dataList).map(key => {
    const element = Object.assign({}, dataList[key]);

    result.push(element);
  });

  return result;
};

const filters = {
  filters: {
  renameLevel,
  nfiExplain(value) {
    if (!value || value.toLowerCase() !== 'nfi') return value;
    return value.replace(/nfi/gi, "National Forest Inventory");
  },
  bytesToSize(bytes) {
    if (typeof bytes == 'number') {
      var sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
      if (bytes == 0) return '0 Byte';
      var i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)));
      return Math.round(bytes / Math.pow(1024, i), 2) + ' ' + sizes[i];
    }
    return '';
  },
  fileType(fileName) {
    if (fileName) {
      var splitedNameItems = fileName.split('.')
      var extension = splitedNameItems[splitedNameItems.length - 1];

      return '[ ' + extension + ' ] ';
    }
    return '';
  },
  sortArrayOfObjectsByName,
},
  methods: {
    renameLevel,
    sortArrayOfObjectsByName,
    summary,
    transformFromObjectToArray,
  }
}
export default filters;