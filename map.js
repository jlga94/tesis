function map(){	
	//var key = Object.keys(this)[0];

	emit(1, // Or put a GROUP BY key here
		{sum: this[word], // the field you want stats for
		min: this[word],
		max: this[word],
		count:1,
		diff: 0, // M2,n:  sum((val-mean)^2)
	});

}