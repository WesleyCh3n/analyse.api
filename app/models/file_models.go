package models

type FltrFile struct {
	Rslt string `json:"rslt" example:"rslt.csv"`
	CyGt string `json:"cyGt" example:"cyGt.csv"`
	CyLt string `json:"cyLt" example:"cyLt.csv"`
	CyRt string `json:"cyRt" example:"cyRt.csv"`
	CyDb string `json:"cyDb" example:"cyDb.csv"`
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
	Path string `json:"ExportFile" example:"exportfile.csv"`
}

type ConcatFile struct {
	Path string `json:"ConcatFile"`
}

type CleanFile struct {
	Path string `json:"CleanFile"`
}
