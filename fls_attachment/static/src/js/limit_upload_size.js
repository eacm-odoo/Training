import { registerPatch } from '@mail/model/model_core';
import { attr } from '@mail/model/model_field';
import Dialog from 'web.Dialog';

var core = require('web.core');
var _t = core._t;

registerPatch({
    name: 'FileUploader',
    recordMethods: {
        /**
        * @override
        */
        async _performUpload({ files }) {

            const attachmentLimit = await this.async(() => this.env.services.rpc({
                model: 'ir.config_parameter',
                method: 'get_param',
                args: ['fls_attachment.attachment_limit'],
            }));

            const limit = parseFloat(attachmentLimit) * 1024 ** 2; // converting to bytes
            let filesWithinLimit = [];

            for (const file of files) {
                if (limit && file.size > limit) {
                    Dialog.alert(this, _t('The file size exceeds the maximum limit of ${attachmentLimit} MB.'), {
                        title: 'Uploading Size Restriction',
                    });
                } else {
                    filesWithinLimit.push(file);
                }
            }

            if (filesWithinLimit.length) {
                await this._super._performUpload({ files: filesWithinLimit });
            }
        },
    }
});
