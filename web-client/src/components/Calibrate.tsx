import * as React from "react";

import { useState } from "react";
import { Camera, Lock, Loader2, AlertCircle, CircleCheckBig} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { AspectRatio } from "@/components/ui/aspect-ratio";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

import {
    Card,
    CardContent,
    CardDescription,
    CardFooter,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";

type CalibrateProps = {
    onImageUpload: (imageFile: File | null) => void;
    onMessage: React.Dispatch<React.SetStateAction<string>>
    message: string
};

function CameraCapture(event: React.ChangeEvent<HTMLInputElement>, setImage: React.Dispatch<React.SetStateAction<string | null>>, setImageFile: React.Dispatch<React.SetStateAction<File | null>>) {
    const file = event.target.files?.[0];

    if (file) {
      setImageFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setImage(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
}

const Calibrate: React.FC<CalibrateProps> = ({ onImageUpload, onMessage, message }) => {
    const [image, setImage] = useState<string | null>(null);
    const [imageFile, setImageFile] = useState<File | null>(null);
    const [loading, setLoading] = useState(false);

    const handleCalibrateClick = async () => {
        if (imageFile) {
                setLoading(true)
                onMessage("Calibrating...")
            try {
                await onImageUpload(imageFile);
                setLoading(false)
            } 
            catch (error) {
                onMessage("Error during calibration");
                console.error("Error during calibration:", error);
            }
        }
    };

    return (
        <div>
            <Card>
                <CardHeader>
                    <AspectRatio ratio={3 / 4}>
                        <div className="border p-4 w-full h-full bg-gray-300 flex items-center justify-center bg-cover bg-center" 
                        style={{ backgroundImage: `url(${image})`}}
                        />
                    </AspectRatio>
                </CardHeader>

                <CardContent className="flex justify-center gap-x-2">
                    <Button onClick={() => document.getElementById('takephoto')?.click()}>
                        <Camera />
                        <input id="takephoto" type="file" accept="image/*" className="hidden" onChange={(e) => CameraCapture(e, setImage, setImageFile)}/>
                    </Button>

                    {image == null ? (
                        <Button disabled variant={"destructive"} className="w-40 flex flex-col items-center justify-center p-2">
                            <Lock />
                        </Button>
                    ) : (
                        <Button
                            onClick={handleCalibrateClick}
                            disabled={loading}
                            className="w-40 flex flex-col items-center justify-center p-2 bg-green-600 hover:bg-green-400 hover:border-green-400"
                        >
                            {loading ? (
                                <div>
                                    <Loader2 className="animate-spin" />
                                </div>
                            ) : (
                                <span>CALIBRATE</span>
                            )}
                        </Button>
                    )}
                </CardContent>

                <CardFooter className="flex items-center justify-center">
                
                
                <Alert>
                {message == "Not Calibrated" || message == "Calibration Failed" || message == "Calibration Timeout" ? (
                    <AlertCircle className="h-4 w-4" />
                ): (
                    <CircleCheckBig className="h-4 w-4" />
                )}
                    <AlertTitle className="p-1">{message}</AlertTitle>
                </Alert>

                </CardFooter>
            </Card>
        </div>
    );
};

export default Calibrate;