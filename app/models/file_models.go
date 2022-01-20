package models

type FltrFile struct {
	Rslt string `json:"rslt"`
	CyGt string `json:"cyGt"`
	CyLt string `json:"cyLt"`
	CyRt string `json:"cyRt"`
	CyDb string `json:"cyDb"`
}

type Range struct {
	Start float32 `json:"Start"`
	End   float32 `json:"End"`
}

type Fltr struct {
	Fltr  FltrFile `json:"FltrFile"`
	Range []Range  `json:"Range"`
}
type ExportFile struct {
	Path string `json:"ExportFile"`
}

type ConcatFile struct {
	Path string `json:"ConcatFile"`
}
