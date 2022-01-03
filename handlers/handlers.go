package handlers

import (
	"fmt"
	"log"

	"github.com/gofiber/fiber/v2"
)

func Pong(c *fiber.Ctx) error {
	res, err := runPython("./file/raw/2021-09-26-18-36_ultium_motion_Dr Tsai_2021.09.26 Dr. Tsai_1.csv", "./file/csv")
	fmt.Print(res)
	fmt.Print(err)
	return c.Status(200).SendString("ok")
}

func UploadFile(c *fiber.Ctx) error {
	file, err := c.FormFile("file")

	if err != nil {
		log.Println("upload error --> ", err)
		return c.JSON(fiber.Map{
			"status":  500,
			"message": "Server error",
			"data":    nil,
		})
	}

	// generate uploadFile from filename and extension
	uploadFile := file.Filename

	// save image to ./file/csv dir
	err = c.SaveFile(file, fmt.Sprintf("./file/csv/%s", uploadFile))

	if err != nil {
		log.Println("image save error --> ", err)
		return c.JSON(fiber.Map{
			"status":  500,
			"message": "Server error",
			"data":    nil,
		})
	}

	outList, err := runPython(fmt.Sprintf("./file/csv/%s", uploadFile), "./file/csv")

	if err != nil {
		log.Println("cannot run python script", err)
		return c.JSON(fiber.Map{
			"status":  500,
			"message": "sub process error",
			"data":    nil,
		})
	}

	// generate image url to serve to client using CDN

	imageUrl := fmt.Sprintf("/file/csv/%s", uploadFile)
	resultUrl := fmt.Sprintf("/%s", outList[0])
	cycleUrl := fmt.Sprintf("/%s", outList[1])

	// create meta data and send to client

	data := map[string]interface{}{

		"imageName": uploadFile,
		"imageUrl":  imageUrl,
		"header":    file.Header,
		"size":      file.Size,
	}

	return c.JSON(fiber.Map{
		"status":    201,
		"message":   "Image uploaded successfully",
		"resultUrl": resultUrl,
		"cycleUrl":  cycleUrl,
		"data":      data,
	})
}
