function finalize(key, value){
	print(JSON.stringify(value));
	return {Sentences:value.sentences};
}