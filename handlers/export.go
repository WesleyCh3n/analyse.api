package handlers

import (
	"encoding/json"
	"fmt"
	"os/exec"
	"strconv"
)

type ReqExport struct {
	RawFile    string `json:"RawFile"`
	ResultFile string `json:"ResultFile"`
	GaitFile   string `json:"GaitFile"`
	Ranges     []struct {
		Start int
		End   int
	} `json:"Ranges"`
}

type ResExport struct {
	ExportFile string `json:"ExportFile"`
}

func exportCsv(r ReqExport, outDir string) (ResExport, error) {
	args := []string{}
	for _, _r := range r.Ranges {
		args = append(args, "-r", strconv.Itoa(_r.Start), strconv.Itoa(_r.End))
	}
	args = append(args, "-f", r.ResultFile, "-c", r.GaitFile, "-s", outDir)

	cmd := exec.Command("./scripts/exporter.py", args...)
	stdout, err := cmd.Output()

	resultExport := ResExport{}
	if err != nil {
		fmt.Println(err.Error())
		return resultExport, err
	}

	json.Unmarshal(stdout, &resultExport)

	return resultExport, err
}
