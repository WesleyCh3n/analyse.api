package utils

import (
	"encoding/json"
	"errors"
	"log"
	"os/exec"
)

func CmdRunner(app string, args []string, result interface{}) error {
	cmd := exec.Command(app, args...)

	out, err := cmd.CombinedOutput()
	if err != nil {
		log.Print(string(out))
		return errors.New(string(out))
	}

	json.Unmarshal(out, &result)

	return err
}
