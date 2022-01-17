package handlers

import (
	"fmt"
	"os/exec"
	"strconv"
)

type ExportJson struct {
	RawFile string `json:"RawFile"`
	Ranges  []struct {
		Start int
		End   int
	} `json:"Ranges"`
}

func exportCsv(e ExportJson) error {
	args := []string{}
	for _, r := range e.Ranges {
		args = append(args, "-r", strconv.Itoa(r.Start), strconv.Itoa(r.End))
	}

	cmd := exec.Command("./scripts/export.py", args...)
	stdout, err := cmd.Output()

	fmt.Print(string(stdout[:]))

	if err != nil {
		fmt.Println(err.Error())
		return err
	}

	// json.Unmarshal(stdout, &resultPath)

	return err
}
