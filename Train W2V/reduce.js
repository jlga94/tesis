function reduce(key, values) {
    var result = {sentences: []};
    //print(JSON.stringify(values));
    for (var i=0; i < values.length; i++){
        var doc = values[i].sentences;
        for (var j=0; j < doc.length; j++){
            result.sentences.push(doc[j]); // will merge sentences from doc to sentencesMerged
        }
    }
    //print(JSON.stringify(result));
    return result;
}