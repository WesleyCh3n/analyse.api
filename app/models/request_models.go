package models

type ReqExport struct {
	Fltr  FltrFile `json:"FltrFile"`
	Range []Range  `json:"RangeIndex"`
}

type ReqConcat struct {
	Files []string `json:"files" example:"[./export1.csv, ./export2.csv]"`
}

type ReqSave struct {
	UploadFile string `json:"uploadFile"`
	Range      string `json:"Range"`
}
