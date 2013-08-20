function check_git() {
	system.log("Checking if GIT is installed...");
	var res = system.run("check_git.sh");
	if (res == 0) {
		system.log("WhooHoo!");
		return true;
	}
	system.log("Nope. it's not...");
	return false;
}