function finalize(key, value){ 
	value.avg = value.sum / value.count;
	value.variance = value.diff / value.count;
	value.stddev = Math.sqrt(value.variance);
	return value;
}