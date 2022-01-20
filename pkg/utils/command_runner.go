package utils

import (
	"encoding/json"
	"os/exec"
)

func CmdRunner(app string, args []string, result interface{}) error {
	cmd := exec.Command(app, args...)

	stdout, err := cmd.Output()
	// fmt.Print(string(stdout))
	if err != nil {
		return err
	}

	json.Unmarshal(stdout, &result)

	return err
}
