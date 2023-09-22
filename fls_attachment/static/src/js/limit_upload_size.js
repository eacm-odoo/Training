/** @odoo-module **/

import { registerPatch } from '@mail/model/model_core';

import Dialog from 'web.Dialog';
import core from 'web.core';
import ajax from 'web.ajax';

const _t = core._t;

registerPatch({
    name: 'FileUploader',
    recordMethods: {
        /**
        * @override
        */
        async _performUpload({ files }) {
            console.log('entering _performUpload override');

            try {
                const attachmentLimit = await ajax.rpc("/web/dataset/call_kw/ir.config_parameter/get_param", {
                    model: 'ir.config_parameter',
                    method: 'get_param',
                    args: ['fls_attachment.attachment_limit'],
                    kwargs: {},
                });
                console.log('attachmentLimit:', attachmentLimit);

                const limit = parseFloat(attachmentLimit) * 1024 ** 2; // converting to bytes
                let filesWithinLimit = [];
                var i = 0;
                for (const file of files) {
                    console.log('file.size:', file.size, i);
                    i++;
                    if (limit && file.size > limit) {
                        Dialog.alert(this, _t(`The file size exceeds the maximum limit of ${attachmentLimit} MB.`), {
                            title: _t('Uploading Size Restriction'),
                        });                        
                    } else {
                        filesWithinLimit.push(file);
                    }
                }
                console.log('filesWithinLimit.length:', filesWithinLimit.length);
                if (filesWithinLimit.length) {
                    return this._super({ files: filesWithinLimit });
                }
            } catch (error) {
                console.error('Error fetching attachment limit:', error);
            }
        },
    }
});
