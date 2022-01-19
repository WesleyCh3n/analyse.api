package models

type FltrFile struct {
	Rslt string `json:"rslt"`
	CyGt string `json:"cyGt"`
	CyLt string `json:"cyLt"`
	CyRt string `json:"cyRt"`
	CyDb string `json:"cyDb"`
}

type Range struct {
	Start int
	End   int
}

type ExportFile struct {
	Path string `json:"ExportFile"`
}

type ConcatFile struct {
	Path string `json:"ConcatFile"`
}
