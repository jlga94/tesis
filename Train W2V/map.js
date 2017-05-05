function map(){	
	var sentencesToReduce = [];//Para quitar las sentences vacias
	for (var i = 0; i < this.Sentences.length; i++) {
		if (this.Sentences[i].length > 0){
			//print(this.Sentences[i]);
			sentencesToReduce.push(this.Sentences[i]);
		}
	}
	emit(1, // Or put a GROUP BY key here
		{sentences: sentencesToReduce} // the field you want stats for
	);

}