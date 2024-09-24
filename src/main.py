# from typing import Tuple, Optional
#
# # python -m pip install maafw
# from maa.define import RectType
# from importlib.metadata import pass_none

from maa.context import Context
from maa.resource import Resource
from maa.controller import AdbController
from maa.tasker import Tasker
from maa.toolkit import Toolkit

from maa.custom_recognition import CustomRecognition
from maa.custom_action import CustomAction


def main():
    user_path = "../assets"
    Toolkit.init_option(user_path)

    resource = Resource()
    res_job = resource.post_path("../assets/resource/base")
    res_job.wait()

    adb_devices = Toolkit.find_adb_devices()
    if not adb_devices:
        print("No ADB device found.")
        exit()

    # for demo, we just use the first device
    device = adb_devices[0]
    controller = AdbController(
        adb_path=device.adb_path,
        address=device.address,
        screencap_methods=device.screencap_methods,
        input_methods=device.input_methods,
        config=device.config,
    )
    print(device)
    controller.post_connection().wait()

    tasker = Tasker()
    tasker.bind(resource, controller)

    if not tasker.inited:
        print("Failed to init MAA.")
        exit()


    resource.register_custom_recognizer("MyRec", MyRecognizer())
    resource.register_custom_action("MyAction", MyAction())

    task_detail = tasker.post_pipeline("StartUpAndClickButton").wait().get()
    # do something with task_detail

    task_detail = tasker.post_recognition("MySingleMatch").wait().get()
    # do something with task_detail

    details = tasker.post_pipeline("test_OCR_1").wait().get()
    print(details)

    detail=tasker.post_action("MyAction").wait().get()
    print(detail)
    print("---- 初始化成功----")


class MyRecognizer(CustomRecognition):

    def analyze(
            self,
            context,
            argv: CustomRecognition.AnalyzeArg,
    ) -> CustomRecognition.AnalyzeResult:
        reco_detail = context.run_recognition(
            "MyCustomOCR",
            argv.image,
            pipeline_override={"MyCustomOCR": {"roi": [100, 100, 200, 300]}},
        )

        # context is a reference, will override the pipeline for whole task
        context.override_pipeline({"MyCustomOCR": {"roi": [1, 1, 114, 514]}})
        # context.run_recognition ...

        # make a new context to override the pipeline, only for itself
        new_context = context.clone()
        new_context.override_pipeline({"MyCustomOCR": {"roi": [100, 200, 300, 400]}})
        reco_detail = new_context.run_recognition("MyCustomOCR", argv.image)

        click_job = context.tasker.controller.post_click(10, 20)
        click_job.wait()

        context.override_next(argv.current_task_name, ["TaskA", "TaskB"])

        return CustomRecognition.AnalyzeResult(
            box=(0, 0, 100, 100), detail="Hello World!"
        )


class MyAction(CustomAction):

    def run(self, context: Context, argv: CustomAction.RunArg) -> CustomAction.RunResult:
        print("hellow")
        return CustomAction.RunResult(True)


if __name__ == "__main__":
    main()
