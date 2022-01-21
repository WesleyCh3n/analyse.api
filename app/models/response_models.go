package models

type ResUpload struct {
	Upload     string `json:"uploadFile" example:"example_raw.csv"`
	ServerRoot string `json:"serverRoot" example:"http://example.com:3000"`
	SaveDir    string `json:"saveDir" example:"file/example"`
	Python     Fltr   `json:"python"`
}

type ResExport struct {
	ServerRoot string     `json:"serverRoot" example:"http://example.com:3000"`
	SaveDir    string     `json:"saveDir" example:"file/example"`
	Python     ExportFile `json:"python"`
}

type ResConcat struct {
	ServerRoot string     `json:"serverRoot" example:"http://example.com:3000"`
	SaveDir    string     `json:"saveDir" example:"file/example"`
	Python     ConcatFile `json:"python"`
}
