package handlers

import (
	"fmt"
	"os/exec"
	"strings"
)

func runPython(csvFile, outDir string) ([]string, error) {
	cmd := exec.Command("./scripts/main.py", "-f", csvFile, "-s", outDir)
	stdout, err := cmd.Output()

	if err != nil {
		fmt.Println(err.Error())
		return []string{}, err
	}
	outFiles := strings.Split(string(stdout), "\n")
	return outFiles, err
}
