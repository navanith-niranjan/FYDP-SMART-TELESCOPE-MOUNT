import * as React from "react"

import { Camera, Upload, DraftingCompass } from "lucide-react"
import { Button } from "@/components/ui/button"
import { AspectRatio } from "@/components/ui/aspect-ratio"

import {
    Card,
    CardContent,
    CardDescription,
    CardFooter,
    CardHeader,
    CardTitle,
  } from "@/components/ui/card"

function CameraCapture(options: boolean) {
    if (options == true){
        document.getElementById('takephoto')?.click();
    }
    else {
        document.getElementById('upload')?.click();
    }
    
}

const Calibrate = () => {
    return (
        <div>
            <Card>
                <CardHeader>
                    <AspectRatio ratio={3 / 4}>
                        <div className="border p-4 w-full h-full bg-gray-300 flex items-center justify-center" />
                    </AspectRatio>
                    
                </CardHeader>

                <CardContent className="flex justify-center gap-x-2">
                    <Button onClick={() => CameraCapture(true)}><Camera /><input id="takephoto" type="file" accept="image/*" capture="environment" className="hidden"/></Button>
                    <Button onClick={() => CameraCapture(false)}><Upload /><input id="upload" type="file" accept="image/*" className="hidden"/></Button>
                </CardContent>

                <CardFooter className="flex justify-center">
                    <Button variant="outline">
                        CALIBRATE
                    </Button>
                </CardFooter>
            </Card>
        </div>
    );
};

export default Calibrate;