package handlers

import (
	"encoding/json"
	"fmt"
	"os/exec"
)

type ReqConcat struct {
	Files []string `json:"Files"`
}

type ResConcat struct {
	ConcatFile string `json:"ConcatFile"`
}

func concatCsv(r ReqConcat, outDir string) (ResConcat, error) {
	args := []string{}
	args = append(args, "-f")
	for _, _r := range r.Files {
		args = append(args, _r)
	}
	args = append(args, "-s", outDir)

	cmd := exec.Command("./scripts/concater.py", args...)
	stdout, err := cmd.Output()

	resultConcat := ResConcat{}
	if err != nil {
		fmt.Println(err.Error())
		return resultConcat, err
	}

	json.Unmarshal(stdout, &resultConcat)

	return resultConcat, err
}
