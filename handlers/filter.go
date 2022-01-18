package handlers

import (
	"encoding/json"
	"fmt"
	"os/exec"
)

type ResFiltered struct {
	RsltCSV string `json:"RsltCSV"`
	CyGtCSV string `json:"CyGtCSV"`
	CyLtCSV string `json:"CyLtCSV"`
	CyRtCSV string `json:"CyRtCSV"`
	CyDbCSV string `json:"CyDbCSV"`
}

func getFilteredData(csvFile, outDir string) (ResFiltered, error) {
	cmd := exec.Command("./scripts/filter.py", "-f", csvFile, "-s", outDir)
	stdout, err := cmd.Output()

	resultPath := ResFiltered{}
	if err != nil {
		fmt.Println(err.Error())
		return resultPath, err
	}

	json.Unmarshal(stdout, &resultPath)

	return resultPath, err
}
